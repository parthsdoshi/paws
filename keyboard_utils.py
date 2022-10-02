from typing import Union, Optional


ESC = "esc"
EMP = None
DEL = "delete"
TAB = "tab"
BAS = "\\"
CAP = "caps lock"
CTR = "ctrl"
RET = "return"
LSH = "shift"
RSH = "right shift"
ALT = "alt"
COM = "command"
SPC = "space"
ROP = "right option"
LEF = "left"
RHT = "right"
UPA = "up"
DWN = "down"
RCO = 54
RCT = "right ctrl"
QWERTY = (
    (ESC, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP, EMP),
    ("`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", DEL),
    (TAB, "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", BAS),
    (CAP, "a", "s", "d", "f", "g", "h", "i", "j", "k", "l", ";", "'", RET),
    (LSH, LSH, "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", RSH, RSH),
    (179, CTR, ALT, COM, SPC, SPC, SPC, SPC, RCO, ROP, LEF, UPA, DWN, RHT),
)


STR_INT = Union[str, int]
NAME_CODE = Optional[STR_INT]
KEYBOARD_FORMAT = tuple[tuple[NAME_CODE, ...], ...]


def generate_parth_override(qwerty_format: KEYBOARD_FORMAT) -> KEYBOARD_FORMAT:
    """Generates Parth's keyboard format from the original qwerty format.

    Args:
        qwerty_format: base qwerty format to change.

    Returns: new parth keyboard format
    """
    assert qwerty_format[3][0] == CAP
    return tuple(tuple(RCT if i == 3 and j == 0 else col for j, col in enumerate(row)) for i, row in enumerate(qwerty_format))


PARTH_QWERTY = generate_parth_override(qwerty_format=QWERTY)
