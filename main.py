import atexit
import logging
import time
from ctypes import CDLL
from threading import Lock
from typing import Iterable, Callable

import keyboard
from keyboard import KeyboardEvent
import rumps
from rumps import MenuItem

from keyboard_utils import PARTH_QWERTY
from rules.events_eligibility_rule import EventsEligibilityRule
from rules.rules import NumEventsNotReleased, EventsWithinNumSeconds, CheckAllAdjacent

# from keyboard._darwinkeyboard import KeyMap


CAT_PAW_DETECTION_RULES = (
    EventsWithinNumSeconds(num_seconds=0.05),
    NumEventsNotReleased(num_events=3),
    CheckAllAdjacent(distance=3, keyboard_fmt=PARTH_QWERTY),
)


START = "Start"
STOP = "Stop"


class PawsStatusBarApp(rumps.App):
    """Defines how the status bar app works."""
    def __init__(self, *args, rules: Iterable[EventsEligibilityRule], detected_callback: Callable[[], None], **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.rules = rules
        self.presses: list[KeyboardEvent] = []
        self.presses_lock = Lock()
        self.kill_paw_detection: Callable = None
        self.detected_callback = detected_callback
        self.start_detection()

    @rumps.clicked(STOP)
    def start_stop(self, sender: MenuItem):
        logging.info(f"Performing {sender.title}")
        if sender.title == START:
            self.start_detection()
        else:
            self.stop_detection()
        sender.title = START if sender.title == STOP else STOP

    def detect_presses(self, rules: Iterable[EventsEligibilityRule], success_callback: Callable[[], None]) -> Callable[[KeyboardEvent], None]:
        """Detect x presses within x seconds.

        Args:
            rules: Rules to check if the last num_presses events match
            success_callback: Calls this if all rules pass.
        """

        def _detect_presses(event: KeyboardEvent) -> None:
            with self.presses_lock:
                self.presses.append(event)

                for rule in rules:
                    passed, self.presses = rule.check(events=self.presses)
                    if not passed:
                        return

                logging.info(f"Presses: {self.presses} made it through. Calling success.")
                success_callback()
                return

        return _detect_presses

    def start_detection(self):
        """Starts paws detection"""
        assert not self.kill_paw_detection, f"Already started!"
        logging.info("Starting detection.")
        self.kill_paw_detection = keyboard.on_press(
            callback=self.detect_presses(
                rules=self.rules,
                success_callback=self.detected_callback,
            ),
        )
        atexit.register(self.kill_paw_detection)

    def stop_detection(self):
        assert self.kill_paw_detection, f"You must start detection before we can stop detection."
        logging.info("Stopping detection.")
        self.kill_paw_detection()
        atexit.unregister(self.kill_paw_detection)
        self.kill_paw_detection = None


LOGIN_DLL = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')


def lock_mac() -> None:
    """Locks MacOS"""
    LOGIN_DLL.SACLockScreenImmediate()
    # Sleep so notification appears on lock screen.
    time.sleep(0.5)
    rumps.notification(title="Pawsed!", subtitle="Paws has locked your laptop!", message=None)


if __name__ == "__main__":
    PawsStatusBarApp(name="\U0001F63A", rules=CAT_PAW_DETECTION_RULES, detected_callback=lock_mac).run()

    # km = KeyMap()
    # print(km.layout_specific_keys)