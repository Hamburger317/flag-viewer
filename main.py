import pathlib
from operator import attrgetter

import pyray as pr

import reader
from draw import draw_flag


def main():
    loaded_flags = []

    flag_folder = pathlib.Path(pr.get_working_directory()) / "flags"

    for path in flag_folder.glob("*.json"):
        with open(path) as file:
            loaded_flags.append(reader.flag_from_json(file.read()))

    loaded_flags.sort(key=attrgetter("category"))

    current = 0
    final_index = len(loaded_flags) - 1
    flag = loaded_flags[current]

    pr.init_window(800, 600, flag.name)

    while not pr.window_should_close():
        if pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT) and current > 0:
            current -= 1

        elif pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT) and current < final_index:
            current += 1

        flag = loaded_flags[current]

        pr.set_window_title(flag.name)

        window = pr.Rectangle(0, 0, pr.get_screen_width(), pr.get_screen_height())

        pr.begin_drawing()
        pr.clear_background(pr.BLANK)

        draw_flag(flag, window)

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
