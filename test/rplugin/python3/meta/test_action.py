from unittest.mock import MagicMock
import pytest
from meta.prompt.action import Action
from meta.action import DEFAULT_ACTION_RULES, DEFAULT_ACTION_KEYMAP


@pytest.fixture
def action():
    action = Action.from_rules(DEFAULT_ACTION_RULES)
    return action


def test_select_next_candidate(meta, action):
    meta.nvim = MagicMock()
    meta.nvim.current.window.cursor = [1, 1]
    action.call(meta, 'meta:select_next_candidate')
    meta.nvim.call.assert_called_with('cursor', [2, 1])


def test_select_previous_candidate(meta, action):
    meta.nvim = MagicMock()
    meta.nvim.current.window.cursor = [2, 1]
    action.call(meta, 'meta:select_previous_candidate')
    meta.nvim.call.assert_called_with('cursor', [1, 1])


def test_switch_matcher(meta, action):
    meta.switch_matcher = MagicMock()
    action.call(meta, 'meta:switch_matcher')
    meta.switch_matcher.assert_called_with()


def test_switch_case(meta, action):
    meta.switch_case = MagicMock()
    action.call(meta, 'meta:switch_case')
    meta.switch_case.assert_called_with()


def test_switch_syntax(meta, action):
    meta.switch_syntax = MagicMock()
    action.call(meta, 'meta:switch_syntax')
    meta.switch_syntax.assert_called_with()
