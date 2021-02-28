from __future__ import annotations

import pytest

from colorado.log import Entry, append_entries


@pytest.mark.parametrize("length_of_log", range(10))
def test_appending_empty_list_of_entries_succeeds(length_of_log: int) -> None:
    log = [Entry(1, 1) for _ in range(length_of_log)]

    assert append_entries(log, previous_index=len(log) - 1, previous_term=1, entries=[])
    assert len(log) == length_of_log


@pytest.mark.parametrize("index_to_replace", range(10))
def test_appending_existing_entry_leaves_log_intact(index_to_replace: int) -> None:
    expected = [Entry(x, x) for x in range(10)]
    actual = expected[:]

    assert append_entries(
        actual,
        previous_index=index_to_replace - 1,
        previous_term=index_to_replace - 1,
        entries=[expected[index_to_replace]],
    )
    assert actual == expected


@pytest.mark.parametrize("size_of_gap", range(1, 11))
def test_appending_fails_with_stale_log(size_of_gap: int) -> None:
    log = [Entry(1, 1)]

    assert not append_entries(
        log,
        previous_index=len(log) + size_of_gap,
        previous_term=1,
        entries=[Entry(2, 1)],
    )
    assert len(log) == 1
    assert log[0] == Entry(1, 1)


@pytest.mark.parametrize("index_to_replace", range(10))
def test_appending_is_idempotent(index_to_replace: int) -> None:
    expected = [Entry(1, x) for x in range(10)]
    actual = expected[:]

    entries = actual[index_to_replace:]

    assert append_entries(
        actual, previous_index=index_to_replace - 1, previous_term=1, entries=entries
    )
    assert actual == expected


@pytest.mark.parametrize("number_of_entries", range(1, 11))
def test_appending_to_empty_log_succeeds(number_of_entries: int) -> None:
    log: list[Entry] = []

    entries = [Entry(1, 1) for _ in range(number_of_entries)]

    assert append_entries(log, previous_index=-1, previous_term=-1, entries=entries)
    assert len(log) == number_of_entries


@pytest.mark.parametrize("number_of_entries", range(1, 11))
def test_appending_to_end_of_log_succeeds(number_of_entries: int) -> None:
    log = [Entry(1, 1) for _ in range(10)]
    expected_length = len(log) + number_of_entries

    # 10 is being added here to make a clear distinction between the
    # entries from the original log and those being appended.
    entries = [Entry(1, x + 10) for x in range(number_of_entries)]

    assert append_entries(
        log, previous_index=len(log) - 1, previous_term=1, entries=entries
    )
    assert len(log) == expected_length
    assert log[-number_of_entries:] == entries


def test_healing_log_with_mismatched_term_fails() -> None:
    expected = [Entry(1, 1), Entry(2, 1)]
    actual = expected[:]

    assert not append_entries(
        actual, previous_index=0, previous_term=2, entries=[Entry(2, 2)]
    )
    assert actual == expected


@pytest.mark.parametrize("number_of_entries", range(1, 11))
def test_part_of_log_can_be_healed(number_of_entries: int) -> None:
    original = [Entry(1, 1) for _ in range(10)]
    actual = original[:]

    entries = [Entry(2, 2) for _ in range(number_of_entries)]

    expected = original[:-1] + entries

    # This will heal the last entry in the log. Subtract 2 to get the
    # index of the entry before it.
    assert append_entries(
        actual, previous_index=len(original) - 2, previous_term=1, entries=entries
    )

    # The length of the new list should be 1 less than the length of the
    assert actual == expected


@pytest.mark.parametrize("length_of_log", range(1, 11))
def test_whole_log_can_be_healed(length_of_log: int) -> None:
    log = [Entry(1, x) for x in range(length_of_log)]

    entries = [Entry(2, 2)]

    assert append_entries(log, previous_index=-1, previous_term=-1, entries=entries)
    assert log == entries
