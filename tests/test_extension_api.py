import pytest

from marvin.extension_api import ExtensionAPI


class FakeRoot:
    def __init__(self):
        self.calls = []

    def after(self, delay, callback):
        self.calls.append((delay, callback))
        return "after-id"


class FakeCompanion:
    def __init__(self):
        self.root = FakeRoot()
        self.notifications = object()
        self._compact_enabled = True
        self._compact_mode = False
        self._reminder_queue = []
        self._bubble_mode = "normal"
        self._bubble_hover = "old"
        self._extension_actions = {}
        self.bubble = "old message"
        self.b_timer = 100
        self.state = "talking"
        self.calls = []

    def say(self, text, state="talking", duration=4000):
        self.calls.append(("say", text, state, duration))
        return "said"

    def _show_marvin(self):
        self.calls.append(("show",))

    def _expand_compact_for_reminder(self):
        self.calls.append(("expand",))


def make_api():
    companion = FakeCompanion()
    return companion, ExtensionAPI(companion)


def test_requires_companion():
    with pytest.raises(ValueError):
        ExtensionAPI(None)


def test_public_state_properties():
    companion, api = make_api()
    assert api.root is companion.root
    assert api.notifications is companion.notifications
    assert api.is_compact_enabled is True
    assert api.is_compact_mode is False
    assert api.has_pending_reminders is False

    companion._reminder_queue.append(("task",))
    companion._compact_mode = True
    assert api.has_pending_reminders is True
    assert api.is_compact_mode is True


def test_legacy_attributes_are_forwarded():
    companion, api = make_api()

    assert api.state == "talking"
    api.state = "alert"
    api.bubble = "legacy message"
    api._bubble_mode = "alert"

    assert companion.state == "alert"
    assert companion.bubble == "legacy message"
    assert companion._bubble_mode == "alert"


def test_say_delegates_to_companion():
    companion, api = make_api()
    result = api.say("Hello", state="alert", duration=1200)
    assert result == "said"
    assert companion.calls == [("say", "Hello", "alert", 1200)]


def test_window_and_compact_actions_delegate():
    companion, api = make_api()
    api.show_marvin()
    api.expand_compact_for_reminder()
    assert companion.calls == [("show",), ("expand",)]


def test_set_bubble_mode():
    companion, api = make_api()
    api.set_bubble_mode("alert")
    assert companion._bubble_mode == "alert"
    assert companion._bubble_hover is None


def test_set_bubble_mode_rejects_empty_value():
    _, api = make_api()
    with pytest.raises(ValueError):
        api.set_bubble_mode(" ")


def test_clear_bubble():
    companion, api = make_api()
    api.clear_bubble()
    assert companion.bubble == ""
    assert companion.b_timer == 0
    assert companion.state == "idle"


def test_schedule_uses_tk_root():
    companion, api = make_api()
    callback = lambda: None
    result = api.schedule(callback, 250)
    assert result == "after-id"
    assert companion.root.calls == [(250, callback)]


def test_schedule_rejects_invalid_arguments():
    _, api = make_api()
    with pytest.raises(TypeError):
        api.schedule("not callable")
    with pytest.raises(ValueError):
        api.schedule(lambda: None, -1)


def test_register_action():
    companion, api = make_api()
    callback = lambda: "opened"
    api.register_action("  GOE dashboard  ", callback)
    assert companion._extension_actions["GOE dashboard"] is callback


def test_register_action_rejects_invalid_arguments():
    _, api = make_api()
    with pytest.raises(ValueError):
        api.register_action("", lambda: None)
    with pytest.raises(TypeError):
        api.register_action("Action", None)


def test_register_action_creates_registry_if_missing():
    companion, api = make_api()
    del companion._extension_actions
    callback = lambda: None
    api.register_action("Action", callback)
    assert companion._extension_actions == {"Action": callback}
