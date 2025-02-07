from typing import Optional
import pyray as pr


def _normalize(value: float) -> int:
    return round(value * 100)


def rgb_to_string(color: pr.Color) -> str:
    r_component = hex(color.r).removeprefix("0x").zfill(2)
    g_component = hex(color.g).removeprefix("0x").zfill(2)
    b_component = hex(color.b).removeprefix("0x").zfill(2)

    code = "#" + r_component + g_component + b_component

    return code.upper()


def hsv_to_string(hsv: pr.Vector3) -> str:
    h_component = str(int(hsv.x)) + "°"
    s_component = str(int(hsv.y * 100)) + "%"
    v_component = str(int(hsv.z * 100)) + "%"

    return ", ".join([h_component, s_component, v_component])


class Spinner:
    def __init__(
        self,
        bounds: Optional[pr.Rectangle]=None,
        label: str = "",
        default: Optional[int] = None,
        minimum: Optional[int] = 0,
        maximum: Optional[int] = 100,
    ):
        self.bounds = bounds
        self.label = label
        self.minimum = minimum
        self.maximum = maximum

        if default is None:
            default = minimum

        self.previous_state = default
        self.pointer = pr.ffi.new("int *", default)

        self.can_edit = False

    @property
    def value(self) -> int:
        if self.pointer[0] > self.maximum:
            return self.maximum
        
        elif self.pointer[0] < self.minimum:
            return self.maximum

        return self.pointer[0]

    @value.setter
    def value(self, value) -> None:
        if value > self.maximum:
            self.pointer[0] = self.maximum
        
        elif value < self.minimum:
            self.pointer[0]
        
        else:
            self.pointer[0] = value
    
    def update_edit_mode(self):
        clicked = pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)
        if not clicked:
            return
        
        mouse_point = pr.get_mouse_position()
        in_bounds = pr.check_collision_point_rec(mouse_point, self.bounds)
        
        if in_bounds:
            self.can_edit = True
        
        else:
            self.can_edit = False
        

    def iterate(self) -> int:
        self.previous_state = self.value
        return self.value

    def reset_to(self, value) -> None:
        self.previous_state = value
        self.value = value

    def has_updated(self) -> bool:
        return self.previous_state != self.value


class ColorPicker:
    def __init__(self, bounds=None, label="") -> None:
        self.bounds = bounds
        self.label = label
        self.previous_state = pr.Vector3(0.0, 1.0, 1.0)
        self.value = pr.Vector3(0.0, 1.0, 1.0)

    def iterate(self) -> pr.Vector3:
        self.previous_state.x = self.value.x
        self.previous_state.y = self.value.y
        self.previous_state.z = self.value.z

        return self.value

    def reset_to(self, hsv) -> None:
        self.previous_state.x = self.value.x = hsv.x
        self.previous_state.y = self.value.y = hsv.y
        self.previous_state.z = self.value.z = hsv.z

    def has_updated(self) -> bool:
        return not pr.vector3_equals(self.previous_state, self.value)

def _necessary_padding(padding_amount, placement):
    return padding_amount * placement if placement != 0 else 0

class AdvancedColorPicker:
    def __init__(self, bounds: pr.Rectangle) -> None:
        self.bounds = bounds

        self.r_spinner = Spinner(label="R", default=255, maximum=255)
        self.g_spinner = Spinner(label="G", default=0, maximum=255)
        self.b_spinner = Spinner(label="B", default=0, maximum=255)
        self.rgb_spinners = (self.r_spinner, self.g_spinner, self.b_spinner)

        self.h_spinner = Spinner(label="H", maximum=359)
        self.s_spinner = Spinner(label="S", default=100)
        self.v_spinner = Spinner(label="V", default=100)
        self.hsv_spinners = (self.h_spinner, self.s_spinner, self.v_spinner)

        self.spinners = self.rgb_spinners + self.hsv_spinners

        for i, spinner in enumerate(self.spinners):
            spinner.bounds = self._get_spinner_position(spinner.label, 0, i)

        self.r: int = self.r_spinner.value
        self.g: int = self.g_spinner.value
        self.b: int = self.b_spinner.value

        self.h: float = self.h_spinner.value
        self.s: float = self.s_spinner.value / 100
        self.v: float = self.v_spinner.value / 100

        self.picker = ColorPicker(bounds)

    def update(self) -> pr.Color:
        for spinner in self.spinners:
            spinner.update_edit_mode()

        if self.picker.has_updated():
            self._update_from_picker()

        elif self.r_spinner.has_updated():
            self._update_from_rgb(self.r_spinner)

        elif self.g_spinner.has_updated():
            self._update_from_rgb(self.g_spinner)

        elif self.b_spinner.has_updated():
            self._update_from_rgb(self.b_spinner)

        elif self.h_spinner.has_updated():
            self._update_from_hsv(self.h_spinner)

        elif self.s_spinner.has_updated():
            self._update_from_hsv(self.s_spinner)

        elif self.v_spinner.has_updated():
            self._update_from_hsv(self.v_spinner)

        return self.current_color

    @property
    def current_color(self) -> pr.Color:
        return pr.Color(self.r, self.g, self.b, 255)

    @property
    def current_color_in_hsv(self) -> pr.Vector3:
        return pr.Vector3(self.h, self.s, self.v)

    def _update_from_picker(self) -> None:
        new_hsv = self.picker.iterate()
        new_color = pr.color_from_hsv(new_hsv.x, new_hsv.y, new_hsv.z)

        self.r = new_color.r
        self.g = new_color.g
        self.b = new_color.b

        self.h = new_hsv.x
        self.s = new_hsv.y
        self.v = new_hsv.z

        self._reset_rgb_spinners_to(new_color)
        self._reset_hsv_spinners_to(new_hsv)

    def _update_from_rgb(self, focus: Spinner) -> None:
        self.r, self.g, self.b = self._read_rgb_spinners(iterate=focus)

        # clean this
        new_hsv = pr.color_to_hsv(self.current_color)
        self.h = new_hsv.x
        self.s = new_hsv.y
        self.v = new_hsv.z

        self._reset_hsv_spinners_to(new_hsv)
        self.picker.reset_to(new_hsv)

    def _update_from_hsv(self, focus: Spinner) -> None:
        self.h, self.s, self.v = self._read_hsv_spinners(iterate=focus)

        new_color = pr.color_from_hsv(self.h, self.s, self.v)
        self.r = new_color.r
        self.g = new_color.g
        self.b = new_color.b

        self._reset_rgb_spinners_to(new_color)
        self.picker.reset_to(pr.Vector3(self.h, self.s, self.v))

    def _read_rgb_spinners(self, iterate: Spinner) -> tuple[int, int, int]:
        return tuple(
            spinner.iterate() if spinner is iterate else spinner.value
            for spinner in self.rgb_spinners
        )

    def _read_hsv_spinners(self, iterate: Spinner) -> tuple[int, int, int]:
        return (
            (
                spinner.iterate() / (1 if spinner is self.h_spinner else 100)
                if spinner is iterate
                else spinner.value / spinner.maximum
            )
            for spinner in self.hsv_spinners
        )

    def _reset_rgb_spinners_to(self, color: pr.Color) -> None:
        self.r_spinner.reset_to(color.r)
        self.g_spinner.reset_to(color.g)
        self.b_spinner.reset_to(color.b)

    def _reset_hsv_spinners_to(self, hsv: pr.Vector3) -> None:
        self.h_spinner.reset_to(int(hsv.x))
        self.s_spinner.reset_to(_normalize(hsv.y))
        self.v_spinner.reset_to(_normalize(hsv.z))
    
    def _get_spinner_position(self, label, x_placement, y_placement):
        placement = pr.Rectangle()

        bar_width = pr.gui_get_style(pr.GuiControl.COLORPICKER,
                                     pr.GuiColorPickerProperty.HUEBAR_WIDTH)
        bar_padding = pr.gui_get_style(pr.GuiControl.COLORPICKER,
                                   pr.GuiColorPickerProperty.HUEBAR_PADDING)
        font_size = pr.gui_get_font().baseSize

        x = self.bounds.x + self.bounds.width + bar_width + (bar_padding * 2)
        x += pr.measure_text(label, font_size)
        x += _necessary_padding(bar_padding, x_placement) + (94 * x_placement)
    
        y = self.bounds.y + (18 * y_placement)
        y += _necessary_padding(bar_padding, y_placement)

        placement.x = x
        placement.y = y
        placement.width = 94
        placement.height = 18
    
        return placement


def draw_color_picker(picker: ColorPicker) -> None:
    pr.gui_color_picker_hsv(picker.bounds, picker.label, picker.value)


def draw_spinner(spinner: Spinner) -> None:
    pr.gui_spinner(
        spinner.bounds,
        spinner.label,
        spinner.pointer,
        spinner.minimum,
        spinner.maximum,
        spinner.can_edit,
    )


def draw_advanced_picker(advanced_color_picker: AdvancedColorPicker) -> None:
    draw_color_picker(advanced_color_picker.picker)

    for spinner in advanced_color_picker.spinners:
        draw_spinner(spinner)


# DEMO
def main() -> None:
    pr.init_window(800, 600, "RGB Sync")
    color_picker = AdvancedColorPicker(pr.Rectangle(10, 50, 150, 150))

    while not pr.window_should_close():
        color = color_picker.update()
        rgb_code = rgb_to_string(color)
        hsv_code = hsv_to_string(color_picker.current_color_in_hsv)
 
        pr.set_window_title(f"RGB Sync | {rgb_code} | {hsv_code}")

        pr.begin_drawing()
        pr.clear_background(color)

        draw_advanced_picker(color_picker)

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
