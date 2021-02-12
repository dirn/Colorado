from __future__ import annotations

from dataclasses import dataclass

from structlog import get_logger

_logger = get_logger()


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
    log_length = len(log)
    number_of_entries = len(entries)

    if previous_index + 1 > log_length:
        # This means the log is stale and needs to be healed.
        _logger.msg(
            "Not appending: previous index not in log.",
            len=log_length,
            number_of_entries=number_of_entries,
            previous_index=previous_index,
        )
        return False

    if previous_index >= 0 and log[previous_index].term != previous_term:
        # This means the log contains records that aren't in the current
        # leader's log and needs to be healed.
        _logger.msg(
            "Not appending: previous term does not match.",
            len=log_length,
            number_of_entries=number_of_entries,
            specified_previous_term=previous_term,
            existing_previous_term=log[previous_index].term,
            previous_index=previous_index,
        )
        return False

    if (
        entries
        and previous_index + 1 < log_length
        and log[previous_index + 1].term != entries[0].term
    ):
        # As part of healing the log, remove the entries that aren't in
        # the current leader's log.
        existing_term = log[previous_index + 1].term  # For the logger.
        del log[previous_index + 1 :]
        _logger.msg(
            "Removed mismatched entries.",
            len=log_length,
            number_of_entries=number_of_entries,
            specified_term=entries[0].term,
            existing_term=existing_term,
            previous_index=previous_index,
        )

    log[previous_index + 1 : previous_index + 1 + number_of_entries] = entries
    _logger.msg(
        "Appended entries",
        len=log_length,
        number_of_entries=number_of_entries,
        new_len=len(log),
    )

    return True
