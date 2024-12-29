import csv
import os
import threading
import traceback
from model import logging, config, cards


CARDS_FILE_PATH = config["cards_file_path"]

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

successful_export = True


def save_image(img, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        img.save(file_path)
    except Exception as e:
        logging.error(f"Failed to save image to {file_path}: {e}\n{traceback.format_exc()}")
        print(f"{RED}Error: Failed to save image to {file_path}.{RESET}")


def run_in_thread_pool(export_function, *args, **kwargs):
    def target_func():
        try:
            export_function(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in thread while executing export function: {e}\n{traceback.format_exc()}")
            print(f"{RED}Error: {e}{RESET}")

    thread = threading.Thread(target=target_func)
    thread.start()
    return thread


def export_data(csv_file, arrays, export_function):
    global data_list
    in_array = False
    open_arrays = []
    print(f"{BLUE}Exporting data...{RESET}")

    for row in csv_file:
        try:
            item_name = row.get('Card Name', row.get('Name', '')).upper()
            if item_name in arrays.values():
                found = False
                for open_array in open_arrays:
                    found = arrays[open_array] == item_name
                    if found:
                        open_arrays.remove(open_array)
                        arrays.pop(open_array)
                        if len(open_arrays) == 0:
                            in_array = False
                        break
                if not found:
                    for key in arrays:
                        if arrays[key] == item_name:
                            arrays.pop(key)
                            break
                run_in_thread_pool(export_function, row)
            elif in_array or type(data_list) is set or item_name in data_list:
                if item_name in data_list:
                    data_list.remove(item_name)
                run_in_thread_pool(export_function, row)
            elif item_name in arrays:
                open_arrays.append(item_name)
                in_array = True
                run_in_thread_pool(export_function, row)
        except Exception as e:
            logging.error(f"Error exporting data for row {row}: {e}\n{traceback.format_exc()}")
            print(f"{RED}Error exporting data for row {row}: {e}{RESET}")


def get_data_list():
    while True:
        try:
            print(f"{YELLOW}Which cards do you want to export?{RESET}")
            print(
                f"{YELLOW}You may specify cards with their name (spaces included).{RESET}\n"
                f"{YELLOW}You can also specify arrays of cards. (e.g., 'Torchic:Lotad')\n"
                f"{YELLOW}Individual cards and arrays of cards are separated by commas. (e.g., 'Torchic,Trapinch:Flygon,Lotad')\n{RESET}"
            )

            user_input = input(
                f"{YELLOW}\nPlease list the cards you wish to export (entering nothing will export all of them): {RESET}"
            ).strip()

            if user_input == '':
                return set()
            return [obj.strip().upper() for obj in user_input.split(",")]

        except ValueError:
            print(f"{RED}Invalid input. Please try again.{RESET}")


def extract_arrays():
    global data_list
    arrays = {}
    for data_id in range(len(data_list) - 1, -1, -1):
        if ":" in data_list[data_id]:
            array = data_list.pop(data_id).split(':')
            arrays[array[0]] = array[1]
    return arrays


def get_csv_data(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='UTF-8') as f:
            return list(csv.DictReader(f, delimiter=','))
    except Exception as e:
        logging.error(f"Failed to read CSV file at {file_path}: {e}\n{traceback.format_exc()}")
        print(f"{RED}Error: Failed to read CSV file at {file_path}.{RESET}")
        return []


def load_data(csv_data, action):
    rows = csv_data
    for row in rows:
        try:
            action(row)
        except Exception as e:
            logging.error(f"Error loading data for row {row}: {e}\n{traceback.format_exc()}")
            print(f"{RED}Error loading data for row {row}: {e}{RESET}")


def export_card(row):
    image = cards.create_card(row)
    if config["export_sorted_by_folder"]:
        save_image(image, f"exports/cards/{row['Type']}/{row['Name']}.png")
    else:
        save_image(image, f"exports/cards/{row['Name']}.png")
    return image


if __name__ == "__main__":
    try:
        data_list = get_data_list()
        data_arrays = extract_arrays()

        export_data(get_csv_data(CARDS_FILE_PATH), data_arrays, export_card)

        if successful_export and len(data_list) != len(data_list) - len(data_arrays) - len(data_list):
            print(f"{YELLOW}\nWarning: Some cards were not able to export.{RESET}")
        else:
            print(f"{GREEN}\nAll cards were exported.{RESET}")

    except Exception as error:
        logging.error('An error occurred: %s', error)
        print(f"{RED}Something went wrong. Check your error.log file for more information.{RESET}")
