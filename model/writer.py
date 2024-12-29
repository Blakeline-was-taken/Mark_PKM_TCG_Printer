
from model.utils import *


SPECIAL_CHARACTERS = {
    "%": "percent", ".": "period", ";": "semicolon", ":": "colon", "'": "apostrophe", ",": "comma",
    "!": "exclamation_mark", "?": "question_mark", "@": "at", "#": "hash", "&": "and", "|": "vertical_bar",
    "*": "asterisk", "-": "dash"
}
OPERATIONS = ["+", "-", "*", "/"]
# Currently useless but you never know
DO_NOT_FUSE = []


def get_operator(op, is_big=False):
    op_file = "bigoperations" if is_big else "operations"
    op_size = 3 * (1 + int(is_big))
    operations_image = Image.open(f"assets/font/{op_file}.png").convert("RGBA")
    width, height = operations_image.size
    version_index = OPERATIONS.index(op)
    left = version_index * op_size
    return operations_image.crop((left, 0, left+op_size, height))


def write_big_number(number):
    final_img = Image.new('RGBA', (6 * len(str(number)), 10))
    ind = 0
    for digit in str(number):
        if digit.isdigit():
            digit_img = Image.open("assets/font/bignumbers.png").convert('RGBA')
            width, height = digit_img.size
            left = int(digit) * 6
            digit_img = digit_img.crop((left, 0, left+6, height))
            final_img.paste(digit_img, (ind, 0), digit_img)
        elif digit in OPERATIONS:
            digit_img = get_operator(digit, is_big=True)
            final_img.paste(digit_img, (ind, 2), digit_img)
        else:
            raise ValueError("Invalid character {}".format(digit))
        ind += 6
    return final_img


def write_number(number):
    number = str(number)
    x_offset = 0
    final_img: Image.Image | None = None
    for digit_id, digit in enumerate(number):
        if digit.isdigit():
            digit_img = Image.open("assets/font/numbers.png").convert('RGBA')
            width, height = digit_img.size
            left = int(digit) * 5
            digit_img = digit_img.crop((left, 0, left+5, height))
        elif digit in OPERATIONS:
            space_left = int(digit_id > 0)
            space_right = int(digit_id < len(number)-1 and number[digit_id+1].isdigit())
            digit_img = Image.new("RGBA", (space_left + 3 + space_right, 7), (0, 0, 0, 0))
            op_img = get_operator(digit)
            digit_img.paste(op_img, (space_left, 0), op_img)
        else:
            raise ValueError("Invalid character {}".format(digit))
        new_final_img = Image.new("RGBA", (x_offset + digit_img.width, 7), (0, 0, 0, 0))
        if final_img:
            new_final_img.paste(final_img, (0, 0), final_img)
        new_final_img.paste(digit_img, (x_offset, 0), digit_img)
        x_offset += digit_img.width
        final_img = new_final_img
    return final_img


def write(text: str, max_length: int, max_height: int = 0, need_first_line_height: bool = False):
    words = text.split()

    line_images = []
    line_img: Image.Image | None = None
    first_line_width = 0  # Yeah, so this is kinda ugly, but basically we need this for the descriptions of moves...

    color = None

    current_line_height = 9
    current_line_width = 0
    final_height = 0
    final_width = 0

    # Write the words and the lines
    word_id = 0
    while word_id < len(words):
        word = words[word_id]
        word_img: Image.Image | None = None
        starting_id = word_id
        # We want to write numbers using the write_number function, so we keep track of the number using this
        writing_number = ""

        #####################
        # Build word image
        #####################

        char_id = 0
        # We can turn this to False if the character should not be able to get fused.
        can_be_fused = True
        while char_id < len(word):
            char = word[char_id]
            # We also have to keep track of whether the last character could be fused.
            last_char_can_be_fused = can_be_fused
            can_be_fused = char not in DO_NOT_FUSE

            def get_char_img():
                nonlocal char, char_id, color, can_be_fused, word, writing_number, current_line_height, line_img, word_img
                # Character is an icon
                if char == "[":

                    # Get icon name
                    char_id += 1
                    icon_name = ""
                    next_char = word[char_id]
                    while next_char != "]":
                        icon_name += next_char
                        char_id += 1
                        next_char = word[char_id]

                    try:
                        # Get icon image
                        if icon_name in config["types"]:
                            character_img = get_type(icon_name)
                        else:
                            try:
                                character_img = write_big_number(icon_name)
                            except ValueError:
                                character_img = Image.open(f"assets/icons/{icon_name}.png").convert("RGBA")
                        # Resize line/word images
                        if character_img.height >= 9 and current_line_height < character_img.height:
                            new_height = character_img.height
                            new_letter_height = max(1, (character_img.height - current_line_height))

                            if line_img:
                                new_line_image = Image.new("RGBA", (current_line_width, new_height), (0, 0, 0, 0))
                                new_line_image.paste(line_img, (0, new_letter_height), line_img)
                                line_img = new_line_image
                            if word_img:
                                new_word_img = Image.new("RGBA", (word_img.width, new_height), (0, 0, 0, 0))
                                new_word_img.paste(word_img, (0, new_letter_height), word_img)
                                word_img = new_word_img

                            current_line_height = new_height
                        can_be_fused = False
                        return character_img
                    except FileNotFoundError:
                        raise ValueError(f"ERROR Icon not found: {icon_name}")

                # Character is a color code  (no character image needed)
                if char_id < len(word) - 1 and char + word[char_id + 1] in COLOR_CONVERSION:
                    return None
                if char_id > 0 and word[char_id - 1] + char in COLOR_CONVERSION:
                    color = word[char_id - 1] + char if word[char_id - 1] + char != "/n" else None
                    return None

                # From here on out, if we have a ValueError, is means the character is unknown.
                try:
                    # Character is a digit
                    if char.isdigit():
                        # Add digit to the number to write
                        writing_number += char
                        if char_id == len(word) - 1 or (char_id < len(word) - 1 and not word[char_id + 1].isdigit()):
                            # Next character is not a digit, so we have the whole number and we can write it
                            character_img = write_number(writing_number)
                            writing_number = ""
                            return character_img
                        return None
                    # Character is an operation we can write
                    if char in OPERATIONS and ((char_id > 0 and word[char_id-1].isdigit()) or (char_id < len(word) - 1 and word[char_id+1].isdigit())):
                        can_be_fused = False
                        return get_operator(char)
                    # Character is an UPPERCASE letter
                    if char.isupper():
                        return Image.open(f"assets/font/{char}.png").convert("RGBA")
                    # Character is a lowercase letter
                    if char.islower():
                        return Image.open(f"assets/font/{char}_min.png").convert("RGBA")
                    # Character is a special character we have an image for
                    if char in SPECIAL_CHARACTERS:
                        can_be_fused = False
                        return Image.open(f"assets/font/{SPECIAL_CHARACTERS[char]}.png").convert("RGBA")

                # Character is unknown
                except ValueError:
                    pass
                return Image.open("assets/font/undefined.png").convert("RGBA")

            # Get character image
            char_img = get_char_img()

            # If we don't have an image for the character, we can skip all the inserting process.
            if char_img is None:
                char_id += 1
                continue

            # Color the character if necessary
            if color:
                set_type(char_img, color)

            next_letter_x_coordinate = word_img.width if word_img else 0

            # Character fusion handling
            def fuse_characters():
                nonlocal next_letter_x_coordinate, word_img, char_img

                can_fuse = 2  # We allow up to 2 pixels of the darkest color to be in the same space.
                fusions_allowed = 2  # We allow a maximum of 2 horizontal pixel shifting
                # If the previous character couldn't be fused, then we still can't.
                # But this one could still be fused with the next, so we don't update can_be_fused.
                if not last_char_can_be_fused:
                    can_fuse = 0

                while can_fuse > 0 and fusions_allowed > 0:
                    for y in range(max(word_img.height, char_img.height)):

                        def pixel_comparison(first_pixel, second_pixel):
                            nonlocal can_fuse
                            # If both pixels have the darkest shade, that's one collision.
                            if first_pixel == second_pixel == (get_colors(color)[3] if color else (51, 44, 80)):
                                can_fuse -= 1

                        try:
                            # We compare the second to last column of pixels from the previous letter
                            # With the first column of pixels from the current letter.
                            pixel_r = word_img.getpixel((next_letter_x_coordinate - 2, y))[:3]
                            pixel_l = char_img.getpixel((0, y))[:3]
                            pixel_comparison(pixel_r, pixel_l)
                            if can_fuse == 0:  # We can't fuse the two characters, so no need to proceed further
                                break

                            # If we are on our second horizontal pixel shift, we have 2 more cases to consider
                            if fusions_allowed == 1:
                                # We compare the last column of pixels from the previous letter
                                # With the second column of pixels from the current letter.
                                pixel_r = word_img.getpixel((next_letter_x_coordinate - 1, y))[:3]
                                pixel_l = char_img.getpixel((1, y))[:3]
                                pixel_comparison(pixel_r, pixel_l)
                                if can_fuse == 0:  # We can't fuse the two characters, so no need to proceed further
                                    break

                                # We do the first comparison again
                                pixel_r = word_img.getpixel((next_letter_x_coordinate - 1, y))[:3]
                                pixel_l = char_img.getpixel((0, y))[:3]
                                # If at any point, we have 2 non-empty pixels colliding with each other
                                if pixel_r != (0, 0, 0) != pixel_l:
                                    can_fuse = 0  # Then we can't perform the second fusion at all.

                        # This exception can (normally) only occur when we exceed one character's height.
                        except IndexError:
                            break

                    if can_fuse > 0:  # We can fuse the 2 characters
                        next_letter_x_coordinate -= 1
                        fusions_allowed -= 1
                        # We set can_fuse back to 2 for the possible second pixel shift.
                        can_fuse = 2

            if word_img and can_be_fused:
                fuse_characters()

            # If we somehow exceed the entirety of the maximum width with a single word, then we can't write it
            if word_img and max_length < next_letter_x_coordinate + char_img.width:
                raise OverflowError(f"Word too long: {word}")

            # Add the character image to the word
            new_word_img = Image.new("RGBA", (char_img.width + next_letter_x_coordinate + int(char_id < len(word)-1), current_line_height), (0, 0, 0, 0))
            if word_img:
                new_word_img.paste(word_img, (0, 0), word_img)
            new_word_img.paste(char_img, (next_letter_x_coordinate, new_word_img.height - 9 - max(0, char_img.height - 9)), char_img)
            word_img = new_word_img

            char_id += 1

        #####################
        # Build line image
        #####################

        # Check if the line width exceeds the limit to move to the next line
        if current_line_width + word_img.width > max_length:
            if len(line_images) == 0 and need_first_line_height:
                first_line_width = current_line_height
            line_images.append(line_img)  # Add current line image to line images
            final_height += current_line_height  # Calculate supposed final height
            # If final height exceeds maximum, raise an error
            if max_height and final_height > max_height:
                raise OverflowError("Text too long: exceeded height limit.")
            final_width = max(final_width, current_line_width)  # Calculate supposed final width
            line_img = None  # Reset current line image
            current_line_height = 9
            current_line_width = 0

            # Reset word (we have to otherwise it will take the settings of the previous line into account)
            word_img = None
            word_id -= 1

        # Add the word image to the line
        if word_img:
            space = (4 if word_id < len(words)-1 else 0)  # This is the " " character !
            new_line_img = Image.new("RGBA", (current_line_width + space + word_img.width, current_line_height), (0, 0, 0, 0))
            if line_img:
                new_line_img.paste(line_img, (0, 0), line_img)
            new_line_img.paste(word_img, (current_line_width, 0), word_img)
            line_img = new_line_img
            current_line_width = line_img.width
            current_line_height = line_img.height

        word_id += 1

    #####################
    # Build final text image
    #####################

    # Add the last line
    if len(line_images) == 0 and need_first_line_height:
        first_line_width = current_line_height
    line_images.append(line_img)
    final_height += current_line_height
    final_width = max(final_width, current_line_width)

    # Create the final image
    final_image = Image.new("RGBA", (final_width, final_height), (0, 0, 0, 0))
    y_offset = 0
    for line in line_images:
        final_image.paste(line, ((final_width - line.width) // 2, y_offset), line)
        y_offset += line.height

    if need_first_line_height:
        return final_image, first_line_width
    else:
        return final_image
