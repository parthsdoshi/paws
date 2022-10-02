import logging
from typing import Iterable, Tuple, FrozenSet, Dict

from keyboard import KeyboardEvent

from keyboard_utils import STR_INT, NAME_CODE, KEYBOARD_FORMAT
from rules.events_eligibility_rule import EventsEligibilityRule


def get_event_id(event: KeyboardEvent) -> STR_INT:
    """Returns event name if present else returns scan_code."""
    return event.name if event.name else event.scan_code


class NumEventsNotReleased(EventsEligibilityRule):
    """Defines an events eligibility rule filtering for events that haven't been released as of yet."""

    def __init__(self, num_events: float) -> None:
        """Initializes rule that filters events to those that are not yet released.

        Args:
            num_events: number of events that haven't been unpressed yet.
        """
        assert num_events
        self.num_events = num_events

    def check(self, events: Iterable[KeyboardEvent]) -> Tuple[bool, Iterable[KeyboardEvent]]:
        """Checks number of events not released is more than num_events."""
        pressed_dict: dict[NAME_CODE, KeyboardEvent] = {}
        for event in events:
            event_id = get_event_id(event=event)
            pressed_dict[event_id] = event

        not_released_events = []
        for event_id, event in pressed_dict.items():
            if event.event_type == "down":
                not_released_events.append(event)

        def _get_time(e: KeyboardEvent) -> float:
            return e.time

        # sort by chronological
        not_released_events = sorted(not_released_events, key=_get_time)[-self.num_events:]
        return True if len(not_released_events) >= self.num_events else False, not_released_events


class EventsWithinNumSeconds(EventsEligibilityRule):
    """Defines an events eligibility rule checking that all events happen within num_seconds."""

    def __init__(self, num_seconds: float) -> None:
        """Initializes rule that all events occurred within number of seconds

        Args:
            num_seconds: number of seconds to look between
        """
        assert num_seconds
        self.num_seconds = num_seconds

    def check(self, events: Iterable[KeyboardEvent]) -> Tuple[bool, Iterable[KeyboardEvent]]:
        """Checks events are within num_seconds."""
        # If there are less than 2 events then all events are always within num_seconds
        if len(events) < 2:
            return True, events

        total_time = 0.
        threshold_violated = False
        # Iterate through events backwards in reverse chronological order
        for i in range(len(events) - 1):
            j = len(events) - 1 - i
            newer_event = events[j]
            older_event = events[j - 1]
            total_time += newer_event.time - older_event.time
            if total_time > self.num_seconds:
                threshold_violated = True
                break

        # this means all events are within num_seconds, return True and leave events as-is
        if not threshold_violated:
            return True, events

        # Threshold was violated -- only keep events that don't violate.
        events = events[j:]

        # If only 1 event left (the newest event), then technically we didn't meet the qualifications of
        # multiple events being within num_seconds.
        if not events or len(events) <= 1:
            return False, events

        return True, events


class CheckAndFixNumEvents(EventsEligibilityRule):
    """Defines an events eligibility rule checking that we're always checking num_events."""

    def __init__(self, num_events: int) -> None:
        """Initializes rule that we're analyzing a constant number of events.

        Args:
            num_events: number of events to analyze
        """
        self.num_events = num_events

    def check(self, events: Iterable[KeyboardEvent]) -> Tuple[bool, Iterable[KeyboardEvent]]:
        """Checks number of events to analyze are equal to num_events."""
        if len(events) < self.num_events:
            return False, events
        # No need to keep more than the latest events so mem footprint stays minimal.
        return True, events[-self.num_events:]


def get_adjacent_keys(x: int, y: int, keyboard_fmt: KEYBOARD_FORMAT, distance: int) -> FrozenSet[NAME_CODE]:
    """Gets adjacent keys to keyboard_fmt[x][y]

    Args:
        x: x coordinate of key to get adjacent of
        y: y coordinate of key to get adjacent of
        keyboard_fmt: keyboard format to look at
        distance: defines how far from current key counts as adjacent

    Returns: frozen set of adjacent keys
    """
    # Set coords to top left of adjacency square. The reason for this is because
    # then we can do less math during the actual for loops.
    top_left_x = x - (distance // 2)
    top_left_y = y - (distance // 2)
    adjacent_keys = set()
    for i in range(distance):
        for j in range(distance):
            x_i = top_left_x + i
            if x_i < 0 or x_i >= len(keyboard_fmt):
                continue
            y_j = top_left_y + j
            if y_j < 0 or y_j >= len(keyboard_fmt[0]):
                continue

            adjacent_keys.add(keyboard_fmt[x_i][y_j])
    return frozenset(adjacent_keys)


def get_adjacency_dict(keyboard_fmt: KEYBOARD_FORMAT, distance: int) -> Dict[NAME_CODE, FrozenSet[NAME_CODE]]:
    """Generates adjacency dictionary for a specific keyboard format and distance."""
    adjacency_matrix = {}
    for i in range(len(keyboard_fmt)):
        for j in range(len(keyboard_fmt[i])):
            # Doesn't handle if the format has the same key multiple times sadly.
            adjacency_matrix[keyboard_fmt[i][j]] = get_adjacent_keys(x=i, y=j, keyboard_fmt=keyboard_fmt, distance=distance)
    return adjacency_matrix


class CheckAllAdjacent(EventsEligibilityRule):
    """Defines an events eligibility rule checking that all events are adjacent within a certain distance."""

    def __init__(self, distance: int, keyboard_fmt: KEYBOARD_FORMAT) -> None:
        """Init

        Args:
            distance: checks that all events are within this distance of each other.
            keyboard_fmt: current keyboard format in use to grab adjacency information for
        """
        self.adj = get_adjacency_dict(keyboard_fmt=keyboard_fmt, distance=distance)

    def check(self, events: Iterable[KeyboardEvent]) -> Tuple[bool, Iterable[KeyboardEvent]]:
        """Checks all events are adjacent to each other."""
        found: set[int] = set()
        for i, event in enumerate(events):
            event_id = get_event_id(event=event)
            adjacent_keys = self.adj.get(event_id)
            if not adjacent_keys:
                logging.warning(f"No adjacent keys found for: {event.name}, {event.scan_code}, {event_id}, {self.adj}. Usually this points to the keyboard format being set incorrectly.")
                continue

            for j, event_b in enumerate(events):
                event_b_id = get_event_id(event=event_b)

                def _found() -> None:
                    if i not in found:
                        found.add(i)
                    if j not in found:
                        found.add(j)

                if event_b_id not in adjacent_keys:
                    continue

                _found()
                if len(found) == len(events):
                    return True, events

        return False, events
