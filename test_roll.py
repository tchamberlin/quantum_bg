from unittest.mock import patch

import pytest

from roll import full_reconfigure


class TestReconfigure:
    def test_nop(self):
        result, actions_remaining, ship_abilities_remaining = full_reconfigure(
            current_ship_die=1,
            desired_ship_die=1,
            ship_abilities_remaining=1,
            actions_remaining=3,
        )

        assert result is True

    @patch("roll.ROLLS", iter([2]))
    def test_3_actions_good_luck(self):
        result, actions_remaining, ship_abilities_remaining = full_reconfigure(
            current_ship_die=1,
            desired_ship_die=2,
            ship_abilities_remaining=1,
            actions_remaining=3,
        )

        assert result is True

    @patch("roll.ROLLS", iter([3, 4, 5]))
    def test_3_actions_bad_luck(self):
        result, actions_remaining, ship_abilities_remaining = full_reconfigure(
            current_ship_die=1,
            desired_ship_die=2,
            ship_abilities_remaining=1,
            actions_remaining=3,
        )

        assert result is False

    @patch("roll.ROLLS", iter([2]))
    def test_0_actions(self):
        result, actions_remaining, ship_abilities_remaining = full_reconfigure(
            current_ship_die=1,
            desired_ship_die=2,
            ship_abilities_remaining=0,
            actions_remaining=0,
        )

        assert result is False
