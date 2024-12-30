from model.writer import *

TYPES = config['types']


def load_cardbase(pkmn_type) -> Image.Image:
    card_base = set_type(Image.open(f"assets/card_template/cardbase.png").convert("RGBA"), pkmn_type)
    type_img = get_type(pkmn_type, pkmn_type)
    card_base.paste(type_img, (81, 6), type_img)
    return card_base


def load_portrait(image, art_file):
    portrait = Image.open(art_file).convert("RGBA")
    image.paste(portrait, (11, 20), portrait)


def print_health(image, health, pkmn_type):
    health = str(health)
    digit_placement = [66, 7]
    for digit_id in range(len(health) - 1, -1, -1):
        digit_img = set_type(write_big_number(health[digit_id]), pkmn_type)
        image.paste(digit_img, tuple(digit_placement), digit_img)
        digit_placement[0] -= 7
    return digit_placement[0] + 7


def print_weakness(image, weakness, pkmn_type):
    weak_type, weakness_affliction = weakness.split("_")
    energy = get_energy(weak_type, pkmn_type)
    image.paste(energy, (9, 117), energy)
    weakness = set_type(write_number(weakness_affliction).convert("RGBA"), pkmn_type)
    image.paste(weakness, (17, 117), weakness)


def print_resistance(image, resistance, pkmn_type):
    resisted_type, resistance_buff = resistance.split("_")
    energy = get_energy(resisted_type, pkmn_type)
    image.paste(energy, (32, 117), energy)
    resistance = set_type(write_number(resistance_buff).convert("RGBA"), pkmn_type)
    image.paste(resistance, (40, 117), resistance)


def print_retreat_cost(image, retreat, pkmn_type):
    energy = get_energy('Normal', pkmn_type)
    for pos_x in range(88-(6 * retreat), 88, 6):
        image.paste(energy, (pos_x, 117), energy)


def print_evolutionary_stage(image, stage, pre_evolution, pkmn_type):
    if stage not in ["Base", "Stage 1", "Stage 2"]:
        raise ValueError("Stage must be one of Base, Stage 1, Stage 2")
    stage_img = set_type(Image.open(f"assets/card_template/{stage}.png"), pkmn_type)
    image.paste(stage_img, (12, 375), stage_img)
    if stage != "Base":
        if pre_evolution == "":
            raise ValueError("Must have a pre evolutionary stage if stage is not Base")
        evo_img = set_type(write(f"Evolves from {pre_evolution}.", 180), pkmn_type)
        image.paste(evo_img, (95, 384), evo_img)


def print_name(image, name, right_border, pkmn_type):
    name_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    limit = right_border - 9
    size_downgrade = 0
    while name_img.height != 9:
        if size_downgrade == 3:
            raise ValueError(f"ERROR Card name is too long : {name}")
        size_downgrade += 1
        try:
            name_img = write(name, limit * size_downgrade)
        except OverflowError:
            pass
    set_type(name_img, pkmn_type)
    if size_downgrade != 3:
        name_img = name_img.resize((name_img.width * (4-size_downgrade), name_img.height * (4-size_downgrade)), Image.NEAREST)
    yname = {1: 24, 2: 27, 3: 30}.get(size_downgrade)
    image.paste(name_img, (24 if limit * (4-size_downgrade) - name_img.width > 3 else 21, yname), name_img)


def get_move_image(move, name_x, pkmn_type):
    energies, name, desc, power = move[0], move[1], move[2], move[3]
    ability = energies == 'Ability'
    name_x = 31 if ability else name_x
    move_img = Image.new("RGBA", (82, 9 if ability else 7), (0, 0, 0, 0))

    if not ability:
        # Print energies
        x_energy = 0
        for energy in energies.split('_'):
            energy_img = get_energy(energy, pkmn_type)
            move_img.paste(energy_img, (x_energy, 0), energy_img)
            x_energy += 6

        # Print attack power
        color = pkmn_type
        if power.startswith('/'):
            if not power.startswith('/n'):
                color = power[:2]
            power = power[2:]

        power_img = Image.open("assets/other/status.png") if power == '0' else write_number(power)
        set_type(power_img, color)
        move_img.paste(power_img, (82-power_img.width, 0), power_img)
        space_left_for_name = 164 - power_img.width
    else:
        # Print ability icon
        ability_img = set_type(Image.open("assets/card_template/ability.png").convert("RGBA"), pkmn_type)
        move_img.paste(ability_img, (0, 0), ability_img)
        space_left_for_name = 164

    # Prepare image for text insertion
    move_img = move_img.resize((move_img.width * 3, move_img.height * 3), Image.NEAREST)

    # Print name
    name_img = write(name, space_left_for_name - name_x * 3)
    name_img = name_img.resize((name_img.width * 2, name_img.height * 2), Image.NEAREST)
    set_type(name_img, pkmn_type)
    move_img.paste(name_img, (name_x * 3, 3 if not ability else 6), name_img)

    # Print description
    if desc != '':
        desc_img, first_line_height = write(desc, 246, need_first_line_height=True)
        set_type(desc_img, pkmn_type)

        spacing_desc = 3 - (first_line_height - 9)
        final_img = Image.new("RGBA", (move_img.width, move_img.height + (3 if ability else 0) + desc_img.height + spacing_desc), (0, 0, 0, 0))
        final_img.paste(move_img, (0, 0), move_img)
        final_img.paste(desc_img, ((246 - desc_img.width) // 2, move_img.height + spacing_desc), desc_img)
        move_img = final_img

    return move_img


def print_moves(image, moves, pkmn_type):
    moves = [move.split('|') for move in moves]
    moves_w_desc = []
    move_images = []

    ability = moves[0][0] == "Ability"
    x_move_name = max(6*len(move[0].split('_'))+5 for move in moves)

    nb_moves = 0
    for move_id, move in enumerate(moves):
        if move != ['']:
            if move[2] != '':
                moves_w_desc.append(move_id)
            move_images.append(get_move_image(move, x_move_name, pkmn_type))
            nb_moves += 1

    if len(move_images) == 0:
        return

    total_move_height = sum(img.height for img_id, img in enumerate(move_images))
    space_left = 120 - total_move_height + (3 if ability else 0)
    spacings = nb_moves+1
    available_spacing = min(9, (space_left // spacings) - (space_left // spacings) % 3) * spacings

    spacing = min(9, max(3, available_spacing // spacings))
    moves_img = Image.new("RGBA", (246, total_move_height + spacing * (nb_moves-1)), (0, 0, 0, 0))
    y_move = 0
    for move_img_id in range(len(move_images)):
        move_img = move_images[move_img_id]
        moves_img.paste(move_img, (0, y_move), move_img)
        y_move += move_img.height - (9 if move_img_id in moves_w_desc else 0)
        if move_img_id < len(move_images) - 1:
            y_move += spacing
            available_spacing -= spacing

    spacings -= nb_moves-1
    image.paste(moves_img, (24, 222 + min(9 if not ability else 6, max(3, available_spacing // spacings))), moves_img)


def print_illustrator(image, illus, pkmn_type):
    illus = "???" if illus == "" else illus
    illus_img = None
    illus_text = ["Illustrated by ", "Illus. by ", "Illus."]
    illus_text_id = 0
    while illus_img is None:
        try:
            illus_img = set_type(write(illus_text[illus_text_id] + illus + ".", 180, 9), pkmn_type)
        except ValueError:
            illus_text_id += 1
            if illus_text_id == len(illus):
                raise ValueError("Illustrator name is too long.")
    image.paste(illus_img, ((180 - illus_img.width) // 2 + 57, 211), illus_img)


def create_card(csv_dict):
    pkmn_type = csv_dict['Type']

    # Load card template
    image = load_cardbase(pkmn_type)

    # Load card portrait
    art_file_card_name = csv_dict['Name'].translate(str.maketrans("", "", " ',-!?"))
    art_file = csv_dict['Art'] if csv_dict['Art'] else f"assets/card_art/{art_file_card_name}.png"
    load_portrait(image, art_file)

    # Print health
    name_right_border = print_health(image, csv_dict['Health'], pkmn_type)

    # Print weakness
    if csv_dict['Weakness'] != "":
        print_weakness(image, csv_dict['Weakness'], pkmn_type)

    # Print resistance
    if csv_dict['Resistance'] != "":
        print_resistance(image, csv_dict['Resistance'], pkmn_type)

    # Print retreat cost
    if csv_dict['Retreat'] != "":
        print_retreat_cost(image, int(csv_dict['Retreat']), pkmn_type)

    # Resize the image
    image = image.resize((image.width * 3, image.height * 3), Image.NEAREST)

    # Print evolutionary stage
    print_evolutionary_stage(image, csv_dict['Stage'], csv_dict['Pre-evolution'], pkmn_type)

    # Print name
    print_name(image, csv_dict['Name'].split("_")[0], name_right_border, pkmn_type)

    # Print moves
    print_moves(image, [csv_dict[f'Move{i}'] for i in range(1, 6)], pkmn_type)

    # Print illustrator
    print_illustrator(image, csv_dict["Illustrator"], pkmn_type)

    return image.resize((image.width * 3, image.height * 3), Image.NEAREST)
