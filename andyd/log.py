from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entry:
    term: int
    item: object


def append_entries(
    log: list[Entry],
    *,
    previous_index: int,
    previous_term: int,
    entries: list[Entry],
) -> bool:
    """Append entries to the log.

    This is both idempotent and destructive. If an entry is identical to
    the entry that already exists at the index, it, along with any
    subsequent entries, will be left intact. If an entry is different,
    though, it, along with any subsequent entries, will be replaced
    provided the first entry being added is from a different term.

    Returns:
        Whether or not the append was successful.
    """
    if previous_index + 1 > len(log):
        # This means the log is stale and needs to be healed.
        return False

    if previous_index >= 0 and log[previous_index].term != previous_term:
        # This means the log contains records that aren't in the current
        # leader's log and needs to be healed.
        return False

    if (
        entries
        and previous_index + 1 < len(log)
        and log[previous_index + 1].term != entries[0].term
    ):
        # As part of healing the log, remove the entries that aren't in
        # the current leader's log.
        del log[previous_index + 1 :]

    log[previous_index + 1 : previous_index + 1 + len(entries)] = entries

    return True
