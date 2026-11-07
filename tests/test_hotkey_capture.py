"""Shortcut capture must distinguish a modifier tap from a chord."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from parlando import engine  # noqa: E402
from parlando.hotkeys import CANCEL_CAPTURE, HotkeyCapture  # noqa: E402


def test_option_space_is_a_chord_not_a_right_option_tap():
    capture = HotkeyCapture()
    assert capture.flags_changed(61, 1 << 19) is None
    assert capture.key_down(49, " ", 1 << 19) == "<alt>+<space>"
    assert capture.flags_changed(61, 0) is None


def test_right_modifier_is_captured_on_release():
    capture = HotkeyCapture()
    assert capture.flags_changed(54, 1 << 20) is None
    assert capture.flags_changed(54, 0) == "cmd_r"


def test_modifier_chord_does_not_become_a_single_tap():
    capture = HotkeyCapture()
    capture.flags_changed(61, 1 << 19)
    capture.flags_changed(60, (1 << 19) | (1 << 17))
    assert capture.flags_changed(60, 1 << 19) is None
    assert capture.flags_changed(61, 0) is None


def test_escape_cancels_and_plain_text_is_not_a_hotkey():
    capture = HotkeyCapture()
    assert capture.key_down(53, "", 0) == CANCEL_CAPTURE
    assert capture.key_down(0, "a", 0) is None
    assert capture.key_down(2, "d", (1 << 20) | (1 << 17)) == "<shift>+<cmd>+d"


def test_captured_key_cannot_start_recording(monkeypatch):
    eng = engine.DictationEngine(engine.Config())
    calls = []
    eng.loop = SimpleNamespace(call_soon_threadsafe=lambda callback: calls.append(callback))
    monkeypatch.setattr(engine.time, "monotonic", lambda: 100)
    eng.begin_hotkey_capture()
    eng.request_toggle()
    assert calls == []
    eng.end_hotkey_capture()
    eng.request_toggle()
    assert calls == []
    monkeypatch.setattr(engine.time, "monotonic", lambda: 100.31)
    eng.request_toggle()
    assert calls == [eng.toggle_action]
