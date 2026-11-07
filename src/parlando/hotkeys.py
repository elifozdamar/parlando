"""Capture a macOS shortcut without treating modifier presses as dictation."""

# NSEvent's device-independent modifier flags and virtual key codes.
MODIFIERS = ((1 << 18, "ctrl"), (1 << 19, "alt"), (1 << 17, "shift"), (1 << 20, "cmd"))
MODIFIER_MASK = sum(flag for flag, _ in MODIFIERS)
RIGHT_MODIFIERS = {54: (1 << 20, "cmd_r"), 60: (1 << 17, "shift_r"),
                   61: (1 << 19, "alt_r"), 62: (1 << 18, "ctrl_r")}
SPECIAL_KEYS = {36: "enter", 48: "tab", 49: "space", 51: "backspace", 53: "esc",
                76: "enter", 117: "delete", 123: "left", 124: "right", 125: "down", 126: "up",
                122: "f1", 120: "f2", 99: "f3", 118: "f4", 96: "f5", 97: "f6", 98: "f7",
                100: "f8", 101: "f9", 109: "f10", 103: "f11", 111: "f12", 105: "f13",
                107: "f14", 113: "f15", 106: "f16", 64: "f17", 79: "f18", 80: "f19", 90: "f20"}
CANCEL_CAPTURE = "__cancel__"


class HotkeyCapture:
    def __init__(self):
        self.pending = None

    def flags_changed(self, code: int, flags: int) -> str | None:
        right = RIGHT_MODIFIERS.get(code)
        if self.pending is not None:
            previous_code, previous_flag, key = self.pending
            if code == previous_code and not flags & previous_flag:
                self.pending = None
                return key if not flags & MODIFIER_MASK else None
        self.pending = None
        if right and flags & MODIFIER_MASK == right[0]:
            self.pending = (code, right[0], right[1])
        return None

    def key_down(self, code: int, characters: str, flags: int) -> str | None:
        self.pending = None
        modifiers = [f"<{name}>" for flag, name in MODIFIERS if flags & flag]
        if code == 53 and not modifiers:
            return CANCEL_CAPTURE
        if not modifiers:
            return None
        special = SPECIAL_KEYS.get(code)
        if special:
            key = f"<{special}>"
        else:
            key = characters.lower()
            if len(key) != 1 or not key.isascii() or not key.isprintable() or key == "+":
                return None
        return "+".join(modifiers + [key])


def shortcut_symbols(value: str) -> str:
    right = {"alt_r": "Right ⌥", "cmd_r": "Right ⌘", "ctrl_r": "Right ⌃", "shift_r": "Right ⇧"}
    if value in right:
        return right[value]
    symbols = {"ctrl": "⌃", "alt": "⌥", "shift": "⇧", "cmd": "⌘",
               "enter": "↩", "space": "Space", "tab": "⇥", "esc": "Esc", "backspace": "⌫",
               "up": "↑", "down": "↓", "left": "←", "right": "→"}
    return " ".join(symbols.get(part.strip("<>"), part.strip("<>").upper())
                    for part in value.split("+"))
