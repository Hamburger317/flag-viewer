from fractions import Fraction

import pyray as pr

from division import Division, DivisionGuide
from draw import draw_division_guide_lines, draw_flag, invert_position
from flag import Flag
from position import Position


def point_in_rectangle(point: pr.Vector2, rectangle: pr.Rectangle):
    x1 = rectangle.x
    y1 = rectangle.y
    width = rectangle.width
    height = rectangle.height

    x2 = x1 + width
    y2 = y1 + height

    return x1 <= point.x <= x2 and y1 <= point.y <= y2


def new_division_from_index(guide, index, color):
    position = Position(float(guide.fraction), index)
    return Division(position, guide.orientation, color, guide.reverse)


def division_index_at_point(guide, click, window):    
    if guide.orientation == "horizontal":
        return division_index_at_point_h(guide, click, window)
    
    elif guide.orientation == "vertical":
        return division_index_at_point_v(guide, click, window)

def division_index_at_point_h(guide, click, window):
    width = window.width
    height = window.height

    fraction = guide.fraction
    reverse = guide.reverse

    space_size = height * fraction

    for i in range(fraction.denominator):
        if reverse:
            start = invert_position(i, space_size, window.height)

        else:
            start = i * space_size
        
        start += window.y

        rectangle = pr.Rectangle(window.x, start, width, space_size)

        if pr.check_collision_point_rec(click, rectangle):
            return i

def division_index_at_point_v(guide, click, window):
    width = window.width
    height = window.height

    fraction = guide.fraction
    reverse = guide.reverse

    space_size = width * fraction

    for i in range(fraction.denominator):
        if reverse:
            start = invert_position(i, space_size, window.width)

        else:
            start = i * space_size

        start += window.x
    
        rectangle = pr.Rectangle(start, window.y, space_size, height)

        if pr.check_collision_point_rec(click, rectangle):
            return i


def create_division(guide, color, window):
    click = pr.get_mouse_position()
    div_index = division_index_at_point(guide, click, window)

    division = new_division_from_index(guide, div_index, color)

    return division


def _update_divisions(guide, color, view, divisions):
    if not pr.check_collision_point_rec(pr.get_mouse_position(), view):
        return divisions

    if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
        division = create_division(guide, color, view)
        return divisions + [division]
    
    return divisions


def _update_orientation(orientation):
    if pr.is_key_pressed(pr.KeyboardKey.KEY_O):
        if orientation == "horizontal":
            return "vertical"
            
        elif orientation == "vertical":
            return "horizontal"
    
    return orientation


def _update_fraction(fraction):
    old_numerator = fraction.numerator
    old_denominator = fraction.denominator

    if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
            return Fraction(old_numerator + 1, old_denominator)
        
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT) and old_numerator > 2:
            return Fraction(old_numerator - 1, old_denominator)

    if pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
        return Fraction(old_numerator, old_denominator + 1)

    elif pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT) and old_denominator > 2:
        return Fraction(old_numerator, old_denominator - 1)
    
    return fraction


def _update_reverse(reverse):
    if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
        return not reverse
    
    return reverse


def _status_text(flag, guide):
    return f"{flag.name} | " \
           f"{len(flag.divisions)} divisions | " \
           f"{guide.fraction.numerator}/{guide.fraction.denominator} | " \
           f"{"Vertical" if guide.orientation == "vertical" else "Horizontal"} | " \
           f"{"Reversed" if guide.reverse else "In-Order"} |"

def main():
    pr.init_window(800, 600, "Editor")

    view = pr.Rectangle((pr.get_screen_width() - 150) / 16, (pr.get_screen_height() - 150) / 2, 150, 150)

    # Default division guide
    guide = DivisionGuide(Fraction(1, 2), "horizontal", False)

    current = pr.Vector3(0, 1.0, 1.0)

    flag = Flag("Unnamed Flag", "", pr.BLACK, [])


    while not pr.window_should_close():
        color = pr.color_from_hsv(current.x, current.y, current.z)

        flag.divisions = _update_divisions(guide, color, view, flag.divisions)
            
        guide.orientation = _update_orientation(guide.orientation)
        guide.fraction = _update_fraction(guide.fraction)
        guide.reverse = _update_reverse(guide.reverse)

        pr.set_window_title(f"Editor")

        pr.begin_drawing()
        pr.clear_background(pr.LIGHTGRAY)

        pr.gui_status_bar((0, 0, pr.get_screen_width(), 24), _status_text(flag, guide))
        pr.gui_color_picker_hsv(pr.Rectangle(0, 400, 150, 150), "KILL ME", current)

        # For previewing purposes
        draw_flag(flag, view)
        
        # For guiding
        draw_division_guide_lines(guide, view, pr.WHITE)

        pr.end_drawing()

    print(flag)

    pr.close_window()


if __name__ == "__main__":
    main()
