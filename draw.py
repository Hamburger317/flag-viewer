from turtle import window_height
import pyray as pr

from division import Division, DivisionGuide
from flag import Flag

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def invert_position(index, bar_size, area):
    return (area - bar_size) - (index * bar_size)


def draw_division(division: Division, window: pr.Rectangle):
    if division.orientation == "horizontal":
        draw_division_h(division, window)

    elif division.orientation == "vertical":
        draw_division_v(division, window)


def draw_division_guide_lines(guide: DivisionGuide, window: pr.Rectangle, color):
    if guide.orientation == "horizontal":
        draw_division_lines_h(guide, window, color)
    
    elif guide.orientation == "vertical":
        draw_division_lines_v(guide, window, color)


def draw_division_lines_h(guide: DivisionGuide, window: pr.Rectangle, color):
    width = window.width
    height = window.height
    fraction = guide.fraction

    space_size = height * fraction

    for i in range(fraction.denominator):
        if guide.reverse:
            y_position = invert_position(i, space_size, window.height)

        else:
            y_position = i * space_size

        # Avoid drawing unhelpful guide line
        if y_position == 0:
            continue

        # Stop drawing out of bound guide lines
        if y_position > window.height or y_position < 0:
            break
        
        line_start = pr.Vector2(window.x, window.y + y_position)
        line_end = pr.Vector2(window.x + width, window.y + y_position)

        pr.draw_line_v(line_start, line_end, color)


def draw_division_lines_v(guide: DivisionGuide, window: pr.Rectangle, color):
    width = window.width
    height = window.height
    fraction = guide.fraction

    space_size = width * fraction

    for i in range(fraction.denominator):
        if guide.reverse:
            x_position = invert_position(i, space_size,  window.width)
        
        else:
            x_position = i * space_size
        
        # Avoid drawing unhelpful guide line
        if x_position == 0:
            continue

        # Stop drawing out of bound guide lines
        if x_position > window.width or x_position < 0:
            break

        line_start = pr.Vector2(window.x + x_position, window.y)
        line_end = pr.Vector2(window.x + x_position, window.y + height)

        pr.draw_line_v(line_start, line_end, color)


def draw_division_h(division: Division, window: pr.Rectangle):
    fraction = division.position.fraction
    index = division.position.index

    bar_size = window.height * fraction

    if division.reverse:
        start = invert_position(index, bar_size, window.height)

    else:
        start = index * bar_size

    # Clamp start and end to match the window's bounds.
    # Only effects non-unit fractions
    # Clamp lower overdraw 
    if start < 0:
        start = 0
        bar_size = window.height - (bar_size * index)
    
    # Clamp upper overdraw
    if start + bar_size > window.height:
        bar_size = min(bar_size, window.height - start)

    bar = pr.Rectangle(window.x, window.y + start, window.width, bar_size)

    pr.draw_rectangle_rec(bar, division.color)


def draw_division_v(division: Division, window: pr.Rectangle):
    fraction = division.position.fraction
    index = division.position.index

    bar_size = window.width * fraction

    if division.reverse:
        start = invert_position(index, bar_size, window.width)

    else:
        start = index * bar_size

    # Clamp start and end to match the window's bounds.
    # Only effects non-unit fractions
    # Clamp lower overdraw 
    if start < 0:
        start = 0
        bar_size = window.width - (bar_size * index)
    
    # Clamp upper overdraw
    if start + bar_size > window.width:
        bar_size = min(bar_size, window.width - start)

    bar = pr.Rectangle(window.x + start, window.y, bar_size, window.height)

    pr.draw_rectangle_rec(bar, division.color)


def draw_flag(flag: Flag, window: pr.Rectangle):
    x = window.x
    y = window.y
    width = window.width
    height = window.height

    background = pr.Rectangle(x, y, width, height)

    pr.draw_rectangle_rec(background, flag.background_color)

    for division in flag.divisions:
        draw_division(division, window)
