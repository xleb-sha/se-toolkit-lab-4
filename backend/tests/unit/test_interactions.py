"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1

def test_filter_excludes_interaction_with_different_learner_and_item_ids() -> None:
    """Boundary case: item_id and learner_id have different values."""
    interactions = [_make_log(1, 2, 1), _make_log(2, 1, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].item_id == 1
    assert result[0].learner_id == 2


def test_filter_returns_multiple_interactions_with_same_item_id() -> None:
    """Edge case: multiple interactions match the same item_id."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 6),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(interaction.item_id == 5 for interaction in result)
    assert [log.id for log in result] == [1, 2, 3]


def test_filter_with_zero_item_id() -> None:
    """Boundary case: item_id is zero."""
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, 1), _make_log(3, 3, 0)]
    result = _filter_by_item_id(interactions, 0)
    assert len(result) == 2
    assert all(interaction.item_id == 0 for interaction in result)
    assert [log.id for log in result] == [1, 3]


def test_filter_with_large_id_values() -> None:
    """Boundary case: very large ID values."""
    large_id = 2**31 - 1  # Max 32-bit signed integer
    interactions = [
        _make_log(large_id, large_id - 1, large_id),
        _make_log(large_id - 1, large_id, large_id - 1),
    ]
    result = _filter_by_item_id(interactions, large_id)
    assert len(result) == 1
    assert result[0].id == large_id
    assert result[0].item_id == large_id


def test_filter_all_interactions_match_filter() -> None:
    """Edge case: all interactions in the list match the filter criterion."""
    interactions = [_make_log(i, i, 999) for i in range(1, 6)]
    result = _filter_by_item_id(interactions, 999)
    assert len(result) == 5
    assert all(interaction.item_id == 999 for interaction in result)
    assert result == interactions


def test_filter_no_interactions_match() -> None:
    """Edge case: filter specifies item_id that doesn't exist in interactions."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2), _make_log(3, 3, 3)]
    result = _filter_by_item_id(interactions, 999)
    assert result == []
    assert len(result) == 0