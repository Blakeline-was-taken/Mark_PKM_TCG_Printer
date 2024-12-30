import tkinter as tk
import traceback
from tkinter import ttk, messagebox, filedialog
import csv
import os
from model import config, logging
from print import export_card
from model.cards import create_card

CARDS_FILE_PATH = config["cards_file_path"]
TYPES = config["types"]
HEADER = ["Name", "Type", "Health", "Weakness", "Resistance", "Retreat", "Stage", "Pre-evolution",
          "Move1", "Move2", "Move3", "Move4", "Move5", "Art", "Illustrator"]


def save_card(card_data):
    # Check if the file already exists
    file_exists = os.path.exists(CARDS_FILE_PATH)
    card_name = card_data[0]  # The card name is the first element of the card data

    # If the file exists, check if the card is already present
    if file_exists:
        with open(CARDS_FILE_PATH, 'r', newline='') as f:
            reader = csv.reader(f)
            existing_cards = [row for row in reader]

        # Check if a card with the same name already exists
        card_exists = False
        for idx, existing_card in enumerate(existing_cards):
            if existing_card[0] == card_name:
                # If the card exists, show a warning message
                card_exists = True
                replace_card = messagebox.askyesno("Warning",
                                                   f"The card '{card_name}' already exists. Do you want to replace it?")
                if not replace_card:
                    return  # Don't add the card if the user doesn't want to replace
                # Replace the card
                existing_cards[idx] = card_data
                break  # Exit the loop after replacing the card

        if not card_exists:
            # If the card doesn't exist, add it normally
            existing_cards.append(card_data)

        # Rewrite all cards in the file, including the replaced or added card
        with open(CARDS_FILE_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(HEADER)  # Add header if it's an empty file
            writer.writerows(existing_cards)

    else:
        # If the file doesn't exist yet, create the file and add the card
        with open(CARDS_FILE_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)  # Add header
            writer.writerow(card_data)

    # Display a success message and ask if the user wants to print the card
    print_card = messagebox.askyesno("Success",
                                     f"Card '{card_name}' added successfully! Would you like to print the card?")

    if print_card:
        try:
            card_data_dict = {}
            for index, item in enumerate(card_data):
                card_data_dict[HEADER[index]] = item
            image = export_card(card_data_dict)
            image.show()  # Show the card image
        except Exception as e:
            logging.error(f"Error while trying to generate {card_name}: {e}\n{traceback.format_exc()}")
            messagebox.showerror("Error", str(e))


def add_move(existing_data=None):
    move_window = tk.Toplevel(root)
    move_window.title("Add or Edit a Move")

    def save_move():
        name = entry_move_name_var.get()
        damage = entry_move_damage_var.get()
        description = entry_move_description_var.get()

        energy_cost = "_".join(energy_list)

        if not name or not damage or not energy_cost:
            messagebox.showerror("Error", "Please fill out all fields for the move.")
            return

        move_data = f"{energy_cost}|{name}|{description}|{damage}"
        if existing_data:
            idx = move_list.index(existing_data)
            move_list[idx] = move_data
            move_listbox.delete(idx)
            move_listbox.insert(idx, name)
        else:
            move_list.append(move_data)
            move_listbox.insert(tk.END, name)
        move_window.destroy()

    # Pre-fill if modifying
    energy_list = []
    entry_move_name_var = tk.StringVar()
    entry_move_description_var = tk.StringVar()
    entry_move_damage_var = tk.StringVar()

    if existing_data:
        parts = existing_data.split("|")
        energy_list = parts[0].split("_")
        entry_move_name_var.set(parts[1])
        entry_move_description_var.set(parts[2])
        entry_move_damage_var.set(parts[3])

    def add_energy():
        energy = combo_energy.get()
        if len(energy_list) < 5 and energy:
            energy_list.append(energy)
            energy_listbox.insert(tk.END, energy)

    def remove_energy():
        selected = energy_listbox.curselection()
        if selected:
            idx = selected[0]
            del energy_list[idx]
            energy_listbox.delete(idx)

    ttk.Label(move_window, text="Move Name:").grid(row=0, column=0, sticky=tk.W)
    entry_move_name = ttk.Entry(move_window, width=30, textvariable=entry_move_name_var)
    entry_move_name.grid(row=0, column=1)

    ttk.Label(move_window, text="Energy Cost:").grid(row=1, column=0, sticky=tk.W)
    combo_energy = ttk.Combobox(move_window, values=TYPES, state="readonly")
    combo_energy.grid(row=1, column=1)
    energy_listbox = tk.Listbox(move_window, height=5, width=30)
    energy_listbox.grid(row=2, column=1)
    for energy in energy_list:
        energy_listbox.insert(tk.END, energy)

    ttk.Button(move_window, text="Add Energy", command=add_energy).grid(row=1, column=2)
    ttk.Button(move_window, text="Remove Energy", command=remove_energy).grid(row=2, column=2)

    ttk.Label(move_window, text="Description:").grid(row=3, column=0, sticky=tk.W)
    entry_move_description = ttk.Entry(move_window, width=30, textvariable=entry_move_description_var)
    entry_move_description.grid(row=3, column=1)

    ttk.Label(move_window, text="Damage:").grid(row=4, column=0, sticky=tk.W)
    entry_move_damage = ttk.Entry(move_window, width=30, textvariable=entry_move_damage_var)
    entry_move_damage.grid(row=4, column=1)

    ttk.Button(move_window, text="Save", command=save_move).grid(row=5, column=0, columnspan=2, pady=10)


def edit_move(event):
    selected = move_listbox.curselection()
    if selected:
        idx = selected[0]
        existing_data = move_list[idx]
        if existing_data.startswith("Ability|"):
            add_ability(existing_data)
        else:
            add_move(existing_data)


def add_ability(existing_data=None):
    ability_window = tk.Toplevel(root)
    ability_window.title("Add or Edit an Ability")

    def save_ability():
        name = entry_ability_name_var.get()
        description = entry_ability_description_var.get()

        if not name or not description:
            messagebox.showerror("Error", "Please fill out all fields for the ability.")
            return

        ability_data = f"Ability|{name}|{description}|0"

        if existing_data:
            idx = move_list.index(existing_data)
            move_list[idx] = ability_data
            move_listbox.delete(idx)
            move_listbox.insert(idx, f"[ABILITY] {name}")
        else:
            # Ajouter le ability au début de la liste
            move_list.insert(0, ability_data)
            move_listbox.insert(0, f"[ABILITY] {name}")
        ability_window.destroy()

    # Fill the fields if we update an existing ability
    entry_ability_name_var = tk.StringVar()
    entry_ability_description_var = tk.StringVar()

    if existing_data:
        parts = existing_data.split("|")
        entry_ability_name_var.set(parts[1])
        entry_ability_description_var.set(parts[2])

    ttk.Label(ability_window, text="Ability Name:").grid(row=0, column=0, sticky=tk.W)
    entry_ability_name = ttk.Entry(ability_window, width=30, textvariable=entry_ability_name_var)
    entry_ability_name.grid(row=0, column=1)

    ttk.Label(ability_window, text="Description:").grid(row=1, column=0, sticky=tk.W)
    entry_ability_description = ttk.Entry(ability_window, width=30, textvariable=entry_ability_description_var)
    entry_ability_description.grid(row=1, column=1)

    ttk.Button(ability_window, text="Save", command=save_ability).grid(row=2, column=0, columnspan=2, pady=10)


def retrieve_card_data():
    # Retrieving form values
    name = entry_name.get()
    identifier = entry_identifier.get()
    if identifier:
        name = name + "_" + identifier
    card_type = combo_type.get()
    health = entry_health.get()
    weakness = combo_weakness.get()
    weakness_multiplier = entry_weakness_multiplier.get() if weakness else ""
    resistance = combo_resistance.get()
    resistance_modifier = entry_resistance_modifier.get() if resistance else ""
    retreat = retreat_spinbox.get()
    stage = combo_stage.get()
    pre_evolution = entry_pre_evolution.get() if stage != "Base" else ""
    art_file = entry_art_file_var.get()
    illustrator = entry_illustrator.get()

    # Validating data
    if not name or not card_type or not health.isdigit() or int(health) <= 0 or (pre_evolution == "" and stage != "Base"):
        messagebox.showerror("Error", "Please correctly fill in all required fields.")
        return

    # Preparing data to save
    if weakness:
        weakness = weakness + "_" + weakness_multiplier
    if resistance:
        resistance = resistance + "_" + resistance_modifier
    card_data = [name, card_type, health, weakness, resistance, retreat, stage, pre_evolution, *move_list]

    # Add empty moves if fewer than 5 moves
    while len(card_data) < 13:
        card_data.append("")

    card_data.append(art_file)
    card_data.append(illustrator)

    return card_data


def submit_form():
    save_card(retrieve_card_data())


def show_card():
    card_data = retrieve_card_data()
    if card_data:
        card_data_dict = {}
        for index, item in enumerate(card_data):
            card_data_dict[HEADER[index]] = item
        image = create_card(card_data_dict)
        image.show()


# Load Pokémon Data button
def load_pokemon_data():
    # Open the CSV file
    try:
        with open(CARDS_FILE_PATH, "r", newline='') as f:
            reader = csv.DictReader(f)
            # Create a list of Pokémon names to choose from
            pokemon_names = [row["Name"] for row in reader]
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{CARDS_FILE_PATH}' not found!")
        return

    # Show a selection dialog
    pokemon_name = tk.simpledialog.askstring("Select Pokémon", "Enter Pokémon Name (with Identifier):", initialvalue="")
    if pokemon_name and pokemon_name not in pokemon_names:
        messagebox.showwarning("Warning", "Pokémon not found in the file!")
        return

    # Load Pokémon data
    try:
        with open(CARDS_FILE_PATH, "r", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Name"] == pokemon_name:
                    # Populate fields with the selected Pokémon data
                    name = row["Name"].split("_", 1)
                    entry_name.delete(0, tk.END)
                    entry_name.insert(0, name[0])
                    entry_identifier.delete(0, tk.END)
                    if len(name) == 2:
                        entry_identifier.insert(0, name[1])
                    combo_type.set(row["Type"])
                    entry_health.delete(0, tk.END)
                    entry_health.insert(0, row["Health"])
                    combo_weakness.set("")
                    combo_resistance.set("")
                    if row["Weakness"]:
                        combo_weakness.set(row["Weakness"].split("_")[0])
                        entry_weakness_multiplier.delete(0, tk.END)
                        entry_weakness_multiplier.insert(0, row["Weakness"].split("_")[1])
                    else:
                        entry_weakness_multiplier.delete(0, tk.END)
                        entry_weakness_multiplier.insert(0, "*2")
                    if row["Resistance"]:
                        combo_resistance.set(row["Resistance"].split("_")[0])
                        entry_resistance_modifier.delete(0, tk.END)
                        entry_resistance_modifier.insert(0, row["Resistance"].split("_")[1])
                    else:
                        entry_resistance_modifier.delete(0, tk.END)
                        entry_resistance_modifier.insert(0, "-20")
                    retreat_spinbox.delete(0, tk.END)
                    retreat_spinbox.insert(0, row["Retreat"])
                    combo_stage.set(row["Stage"])
                    entry_pre_evolution.delete(0, tk.END)
                    entry_pre_evolution.insert(0, row["Pre-evolution"])
                    move_list.clear()
                    move_listbox.delete(0, tk.END)
                    for move_id in range(1, 6):
                        move = row[f"Move{move_id}"]
                        if move:
                            move_list.append(move)
                            move_data = move.split("|")
                            move_listbox.insert(tk.END, ("[ABILITY] " if move_data[0] == "Ability" else "") + move_data[1])
                    entry_art_file_var.set(row["Art"])
                    entry_illustrator.delete(0, tk.END)
                    entry_illustrator.insert(0, row["Illustrator"])
                    break
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Creating the main window
root = tk.Tk()
root.title("Add Card")

# Form fields
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

# Load Pokémon Data
ttk.Button(frame, text="Load Pokémon Data", width=82, command=load_pokemon_data).grid(row=0, column=0, pady=5, sticky=tk.W, columnspan=4)

# Card name
ttk.Label(frame, text="Card Name:").grid(row=1, column=0, sticky=tk.W)
entry_name = ttk.Entry(frame, width=30)
entry_name.grid(row=1, column=1)

# Card identifier
ttk.Label(frame, text="Identifier:").grid(row=1, column=2, sticky=tk.W)
entry_identifier = ttk.Entry(frame, width=20)
entry_identifier.grid(row=1, column=3)

# Card type
ttk.Label(frame, text="Card Type:").grid(row=2, column=0, sticky=tk.W)
combo_type = ttk.Combobox(frame, values=TYPES, state="readonly")
combo_type.grid(row=2, column=1)

# Health points
ttk.Label(frame, text="Health Points (HP):").grid(row=3, column=0, sticky=tk.W)
entry_health = ttk.Spinbox(frame, from_=1, to=999, width=10)
entry_health.grid(row=3, column=1)

# Weakness
ttk.Label(frame, text="Weakness:").grid(row=4, column=0, sticky=tk.W)
weakness_var = tk.StringVar(value="")
combo_weakness = ttk.Combobox(frame, textvariable=weakness_var, values=[""] + TYPES, state="readonly")
combo_weakness.grid(row=4, column=1)
ttk.Label(frame, text="Multiplier:").grid(row=4, column=2, sticky=tk.W)
entry_weakness_multiplier = ttk.Entry(frame, width=10)
entry_weakness_multiplier.insert(0, "*2")
entry_weakness_multiplier.configure(state="disabled")
entry_weakness_multiplier.grid(row=4, column=3)


# Update state of Weakness Multiplier based on Weakness selection
def update_weakness_multiplier(*args):
    if weakness_var.get() == "":  # If "" is selected, disable the Multiplier field
        entry_weakness_multiplier.configure(state="disabled")
        entry_weakness_multiplier.delete(0, tk.END)
    else:  # Enable the field otherwise
        entry_weakness_multiplier.configure(state="normal")
        if entry_weakness_multiplier.get() == "":
            entry_weakness_multiplier.insert(0, "*2")


# Trace changes to the Weakness variable
weakness_var.trace("w", update_weakness_multiplier)

# Resistance
ttk.Label(frame, text="Resistance:").grid(row=5, column=0, sticky=tk.W)
resistance_var = tk.StringVar(value="")
combo_resistance = ttk.Combobox(frame, textvariable=resistance_var, values=[""] + TYPES, state="readonly")
combo_resistance.grid(row=5, column=1)
ttk.Label(frame, text="Modifier:").grid(row=5, column=2, sticky=tk.W)
entry_resistance_modifier = ttk.Entry(frame, width=10)
entry_resistance_modifier.insert(0, "-20")
entry_resistance_modifier.configure(state="disabled")
entry_resistance_modifier.grid(row=5, column=3)


# Update state of Resistance Modifier based on Resistance selection
def update_resistance_modifier(*args):
    if resistance_var.get() == "":  # If "" is selected, disable the Modifier field
        entry_resistance_modifier.configure(state="disabled")
        entry_resistance_modifier.delete(0, tk.END)
    else:  # Enable the field otherwise
        entry_resistance_modifier.configure(state="normal")
        if entry_resistance_modifier.get() == "":
            entry_resistance_modifier.insert(0, "-20")


# Trace changes to the Resistance variable
resistance_var.trace("w", update_resistance_modifier)

# Retreat cost
ttk.Label(frame, text="Retreat Cost:").grid(row=6, column=0, sticky=tk.W)
retreat_spinbox = ttk.Spinbox(frame, from_=0, to=4, width=10)
retreat_spinbox.grid(row=6, column=1)

# Stage
ttk.Label(frame, text="Stage:").grid(row=7, column=0, sticky=tk.W)
stage_var = tk.StringVar(value="Base")
combo_stage = ttk.Combobox(frame, textvariable=stage_var, values=["Base", "Stage 1", "Stage 2"], state="readonly")
combo_stage.grid(row=7, column=1)

# Pre-evolution
ttk.Label(frame, text="Pre-evolution:").grid(row=7, column=2, sticky=tk.W)
entry_pre_evolution = ttk.Entry(frame, width=20, state="disabled")
entry_pre_evolution.grid(row=7, column=3)


# Update state of Pre-evolution entry based on Stage selection
def update_pre_evolution_state(*args):
    if stage_var.get() == "Base":
        entry_pre_evolution.configure(state="disabled")
        entry_pre_evolution.delete(0, tk.END)  # Clear the value if switching back to Base
    else:
        entry_pre_evolution.configure(state="normal")


stage_var.trace("w", update_pre_evolution_state)

# Moves
ttk.Label(frame, text="Moves:").grid(row=8, column=0, sticky=tk.W)
move_list = []
move_listbox = tk.Listbox(frame, height=5, width=30)
move_listbox.grid(row=8, column=1, rowspan=2)
move_listbox.bind("<Double-Button-1>", edit_move)
ttk.Button(frame, text="Add a Move", command=add_move).grid(row=8, column=2, columnspan=2)
ttk.Button(frame, text="Add an Ability", command=add_ability).grid(row=9, column=2, columnspan=2)

# Portrait file explanation
ttk.Label(frame, text="NOTE : By default, the file used will be : assets/card_art/CARDNAME_IDENTIFIER.png").grid(row=10, column=0, sticky=tk.W, columnspan=4)

# Portrait file
ttk.Label(frame, text="Portrait File:").grid(row=11, column=0, sticky=tk.W)
entry_art_file_var = tk.StringVar()
ttk.Button(frame, text="Choose File (optional)", command=lambda: entry_art_file_var.set(filedialog.askopenfilename())).grid(row=11, column=1)
ttk.Entry(frame, textvariable=entry_art_file_var, state="readonly", width=30).grid(row=11, column=2, columnspan=2)

# Illustrator
ttk.Label(frame, text="Illustrator:").grid(row=12, column=0, sticky=tk.W)
entry_illustrator = ttk.Entry(frame, width=30)
entry_illustrator.grid(row=12, column=1)

# Submit button
btn_submit = ttk.Button(frame, text="Add Card", command=submit_form)
btn_submit.grid(row=13, column=1, pady=10)

# Show card button
btn_show_card = ttk.Button(frame, text="Show Card", command=show_card)
btn_show_card.grid(row=13, column=2, columnspan=2, pady=10)

root.mainloop()
