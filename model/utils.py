from PIL import Image
from model import config


TYPES = config["types"]
COLOR_CONVERSION = {
    "/r": [(249, 187, 178), (249, 187, 178), (249, 97, 97), (206, 46, 46)],
    "/g": [(181, 249, 178), (181, 249, 178), (94, 245, 86), (45, 186, 38)],
    "/b": [(178, 249, 245), (178, 249, 245), (85, 244, 237), (46, 175, 204)],
    "/y": [(243, 250, 177), (243, 250, 177), (235, 227, 53), (203, 155, 17)],
    "/p": [(234, 177, 250), (234, 177, 250), (198, 109, 223), (141, 24, 173)],
    "/o": [(250, 222, 177), (250, 222, 177), (222, 151, 38), (173, 116, 24)],
    "/w": [(241, 235, 217), (241, 235, 217), (168, 164, 151), (130, 127, 119)],
    "/n": None
}


def get_type_variant(image, pkmn_type):
    if pkmn_type not in TYPES:
        raise ValueError(f"'{pkmn_type}' is not a valid type.")
    width, height = image.size
    version_height = width // len(TYPES)
    version_index = TYPES.index(pkmn_type)
    left = version_index * version_height
    right = (version_index + 1) * version_height
    return image.crop((left, 0, right, height))


def replace_colors(img, old_colors, new_colors):
    img.putdata([
        new_colors[old_colors.index(pixel[:len(old_colors[0])])] if pixel[:len(old_colors[0])] in old_colors else pixel
        for pixel in list(img.getdata())
    ])
    return img


def get_type_colors(pkmn_type):
    if pkmn_type not in TYPES:
        raise ValueError(f"'{pkmn_type}' is not a valid type.")
    colors = list(get_type_variant(Image.open("assets/card_template/typecolors.png"), pkmn_type).getdata()) + [(51, 44, 80)]
    return colors


def set_type(img, pkmn_type):
    if pkmn_type not in TYPES:
        if pkmn_type in COLOR_CONVERSION:
            replace_colors(img, config["base_colors"], get_colors(pkmn_type))
            return img
        raise ValueError(f"'{pkmn_type}' is not a valid type.")
    replace_colors(img, config["base_colors"], get_type_colors(pkmn_type))
    return img


def get_colors(color):
    if color not in COLOR_CONVERSION:
        raise ValueError(f"'{color}' is not a valid color.")
    return COLOR_CONVERSION.get(color, [])


def get_energy(pkmn_type, card_type=None) -> Image.Image:
    energy_img = get_type_variant(Image.open(f"assets/card_template/energies.png").convert("RGBA"), pkmn_type).convert("RGBA")
    if card_type:
        replace_colors(energy_img, [config["base_colors"][2]], [get_type_colors(card_type)[2]])
    return energy_img


def get_type(pkmn_type, card_type=None) -> Image.Image:
    type_img = get_type_variant(Image.open(f"assets/card_template/types.png").convert("RGBA"), pkmn_type).convert("RGBA")
    if card_type:
        replace_colors(type_img, [config["base_colors"][2]], [get_type_colors(card_type)[2]])
    return type_img
