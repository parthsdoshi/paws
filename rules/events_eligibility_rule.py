from typing import Protocol, Iterable, Tuple

from keyboard import KeyboardEvent


class EventsEligibilityRule(Protocol):
    """Defines a protocol for to check if a collection of events meets a rule's criteria."""

    def check(self, events: Iterable[KeyboardEvent]) -> Tuple[bool, Iterable[KeyboardEvent]]:
        """Calls the rule eligibility checker.

        Args:
            events: events to check

        Returns: A tuple containing:
            * if the events passed the check
            * a maybe-modified events iterable for downstream rules to use
        """
