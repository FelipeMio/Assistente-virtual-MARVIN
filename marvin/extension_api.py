"""Stable public interface for MARVIN extensions."""


class ExtensionAPI:
    """Facade that keeps extensions away from companion internals."""

    def __init__(self, companion):
        if companion is None:
            raise ValueError("companion is required")
        object.__setattr__(self, "_companion", companion)

    def __getattr__(self, name):
        """Temporary compatibility for extensions not yet migrated."""
        return getattr(self._companion, name)

    def __setattr__(self, name, value):
        """Forward legacy extension writes to the host application."""
        if name == "_companion":
            object.__setattr__(self, name, value)
        else:
            setattr(self._companion, name, value)

    @property
    def root(self):
        """Tk root, exposed for extension-owned windows and callbacks."""
        return self._companion.root

    @property
    def notifications(self):
        """Current notification manager, or None before initialization."""
        return getattr(self._companion, "notifications", None)

    @property
    def is_compact_enabled(self):
        return bool(self._companion._compact_enabled)

    @property
    def is_compact_mode(self):
        return bool(self._companion._compact_mode)

    @property
    def has_pending_reminders(self):
        return bool(self._companion._reminder_queue)

    def say(self, text, state="talking", duration=4000):
        """Display a message using the companion speech bubble."""
        return self._companion.say(
            text,
            state=state,
            duration=duration,
        )

    def show_marvin(self):
        """Bring the MARVIN window to the foreground."""
        return self._companion._show_marvin()

    def expand_compact_for_reminder(self):
        """Expand compact mode using the existing reminder behavior."""
        return self._companion._expand_compact_for_reminder()

    def set_bubble_mode(self, mode, hover=None):
        """Set the interaction mode of the speech bubble."""
        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("mode must be a non-empty string")

        self._companion._bubble_mode = mode
        self._companion._bubble_hover = hover

    def clear_bubble(self):
        """Clear the current bubble and return the companion to idle."""
        self._companion.bubble = ""
        self._companion.b_timer = 0
        self._companion.state = "idle"

    def schedule(self, callback, delay_ms=0):
        """Schedule a callback on the Tk main thread."""
        if not callable(callback):
            raise TypeError("callback must be callable")

        delay = int(delay_ms)
        if delay < 0:
            raise ValueError("delay_ms cannot be negative")

        return self.root.after(delay, callback)

    def register_action(self, name, callback):
        """Register an action shown by MARVIN's extension action UI."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not callable(callback):
            raise TypeError("callback must be callable")

        actions = getattr(
            self._companion,
            "_extension_actions",
            None,
        )
        if actions is None:
            actions = {}
            self._companion._extension_actions = actions

        actions[name.strip()] = callback
