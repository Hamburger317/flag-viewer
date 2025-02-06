import json
from fractions import Fraction

import pyray as pr

from division import Division
from flag import Flag
from position import Position


def parse_hex_code(s):
    return pr.get_color(int(s.removeprefix("#"), 16))


def parse_fraction(s):
    return Fraction(s)


def unpack_position(unparsed_position):
    fraction = parse_fraction(unparsed_position["fraction"])
    index = unparsed_position["index"]

    return Position(fraction, index)


def parse_divisions(unparsed_divisions):
    divisions = []

    for division in unparsed_divisions:
        partition = unpack_position(division["position"])
        orientation = division["orientation"]
        color = parse_hex_code(division["color"])
        reverse = division.get("reverse", False)

        divisions.append(Division(partition, orientation, color, reverse))

    return divisions


def flag_from_json(data):
    flag_data = json.loads(data)

    name = flag_data.get("name", "")
    category = flag_data.get("category", "")
    divisions = parse_divisions(flag_data.get("divisions", []))
    background_color = flag_data.get("background_color", pr.BLACK)

    if isinstance(background_color, str):
        background_color = parse_hex_code(background_color)

    return Flag(name, category, background_color, divisions)
