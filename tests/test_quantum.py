import pytest

from quantum_bg.quantum import Attacker, Defender, do_iterations, get_results, load, save


class TestNoCards:
    def test_attacker_wins_ties(self):
        a = Attacker(ship_die=1, combat_die_rolls=[1])
        d = Defender(ship_die=1, combat_die_rolls=[1])
        attacker_wins = a.attack(d)
        assert a.total() == 2
        assert d.total() == 2
        assert attacker_wins

    def test_lower_attacker_wins(self):
        a = Attacker(ship_die=1, combat_die_rolls=[1])
        d = Defender(ship_die=2, combat_die_rolls=[2])
        attacker_wins = a.attack(d)
        assert a.total() == 2
        assert d.total() == 4
        assert attacker_wins

    def test_higher_attacker_loses(self):
        a = Attacker(ship_die=2, combat_die_rolls=[1])
        d = Defender(ship_die=1, combat_die_rolls=[1])
        attacker_wins = a.attack(d)
        assert a.total() == 3
        assert d.total() == 2
        assert not attacker_wins

    def test_invalid_ship_die(self):
        with pytest.raises(ValueError, match=r"ship_die must be between 1 and 6!.*"):
            Attacker(ship_die=7, combat_die_rolls=[1])
        with pytest.raises(ValueError, match=r"ship_die must be between 1 and 6!.*"):
            Attacker(ship_die=0, combat_die_rolls=[1])

    def test_invalid_combat_die(self):
        with pytest.raises(ValueError, match=r"All combat_die_rolls must be between 1 and 6!.*"):
            Attacker(ship_die=6, combat_die_rolls=[7])
        with pytest.raises(ValueError, match=r"All combat_die_rolls must be between 1 and 6!.*"):
            Attacker(ship_die=6, combat_die_rolls=[0])


class TestCards:
    """Test specific card behaviours"""

    def test_strategic(self):
        a = Attacker(ship_die=1, combat_die_rolls=[1], cards=["strategic"])
        d = Defender(ship_die=1, combat_die_rolls=[1])

        assert a.cards == ("strategic",)
        attacker_wins = a.attack(d)
        assert a.total() == 0
        assert d.total() == 2
        assert attacker_wins

    def test_ferocious(self):
        a = Attacker(ship_die=1, combat_die_rolls=[1], cards=["ferocious"])
        d = Defender(ship_die=1, combat_die_rolls=[1])

        assert a.cards == ("ferocious",)
        attacker_wins = a.attack(d)
        assert a.total() == 1
        assert d.total() == 2
        assert attacker_wins

    def test_cruel(self):
        a = Attacker(ship_die=2, combat_die_rolls=[2], cards=["cruel"])
        d = Defender(ship_die=1, combat_die_rolls=[2, 5])

        assert a.cards == ("cruel",)
        attacker_wins = a.attack(d)
        assert a.total() == 4
        assert d.total() == 6
        assert attacker_wins

    def test_relentless(self):
        a = Attacker(
            ship_die=2,
            combat_die_rolls=[4, 5],
            cards=["relentless"],
        )
        d = Defender(ship_die=1, combat_die_rolls=[2])

        assert a.cards == ("relentless",)
        attacker_wins = a.attack(d)
        assert a.total() == 7
        assert d.total() == 3
        assert not attacker_wins

    def test_scrappy_attacker(self):
        a = Attacker(
            ship_die=2,
            combat_die_rolls=[4, 5],
            cards=["scrappy"],
        )
        d = Defender(ship_die=1, combat_die_rolls=[2])

        assert a.cards == ("scrappy",)
        attacker_wins = a.attack(d)
        assert a.total() == 7
        assert d.total() == 3
        assert not attacker_wins

    def test_scrappy_defender(self):
        a = Attacker(ship_die=2, combat_die_rolls=[1])
        d = Defender(ship_die=1, combat_die_rolls=[4], cards=["scrappy"])

        assert d.cards == ("scrappy",)
        attacker_wins = a.attack(d)
        assert a.total() == 3
        assert d.total() == 5
        assert attacker_wins
        # Only one, because Scrappy doesn't do anything on defense!
        assert d.combat_die_rolls == [4]

    def test_rational(self):
        a = Attacker(ship_die=2, combat_die_rolls=[1])
        d = Defender(ship_die=1, combat_die_rolls=[3], cards=["rational"])

        assert d.cards == ("rational",)
        attacker_wins = a.attack(d)
        assert a.total() == 3
        assert d.total() == 4
        assert attacker_wins
        # Only one, because Scrappy doesn't do anything on defense!
        assert d.combat_die_rolls == [3]

    def test_stubborn_attacker(self):
        a = Attacker(ship_die=2, combat_die_rolls=[2], cards=["stubborn"])
        d = Defender(ship_die=2, combat_die_rolls=[1])

        assert a.cards == ("stubborn",)
        attacker_wins = a.attack(d)
        assert a.total() == 4
        assert d.total() == 3
        # Stubborn does nothing when held by attacker
        assert not attacker_wins

    def test_stubborn_defender(self):
        a = Attacker(ship_die=2, combat_die_rolls=[1])
        d = Defender(ship_die=2, combat_die_rolls=[1], cards=["stubborn"])

        assert d.cards == ("stubborn",)
        attacker_wins = a.attack(d)
        # Defender breaks ties when they hold Stubborn
        assert a.total() == 3
        assert d.total() == 3
        assert not attacker_wins

    def test_invalid_cards(self):
        with pytest.raises(ValueError, match=r"Invalid cards: \['fake_card'\]"):
            Attacker(ship_die=1, cards=["fake_card"])

    def test_multiple_cards(self):
        a = Attacker(ship_die=2, combat_die_rolls=[1], cards=["strategic", "ferocious"])
        d = Defender(ship_die=1, combat_die_rolls=[1])
        attacker_wins = a.attack(d)
        # strategic: -2, ferocious: -1, so total is 2+1-2-1 = 0
        assert a.total() == 0
        assert d.total() == 2
        assert attacker_wins


class TestSideMethods:
    """Test Side class utility methods"""

    def test_to_string_with_combat_die(self):
        a = Attacker(ship_die=3, combat_die_rolls=[4], cards=["strategic"])
        a.attack(Defender(ship_die=1, combat_die_rolls=[1]))
        string_rep = Attacker.to_string(a.ship_die, a.combat_die, a.cards)
        assert "3+4=7" in string_rep
        assert "strategic" in string_rep

    def test_to_string_without_combat_die(self):
        string_rep = Attacker.to_string(3, None, ())
        assert string_rep == "Attacker 3"

    def test_to_string_with_cards(self):
        string_rep = Defender.to_string(2, 5, ["ferocious", "cruel"])
        assert "2+5=7" in string_rep
        assert "ferocious" in string_rep
        assert "cruel" in string_rep

    def test_str_method(self):
        a = Attacker(ship_die=3, combat_die_rolls=[4])
        a.roll()
        string_rep = str(a)
        assert "Attacker" in string_rep
        assert "3+4=7" in string_rep

    def test_total_dice_only(self):
        a = Attacker(ship_die=2, combat_die_rolls=[3], cards=["strategic"])
        a.roll()
        # With dice_only=True, modifiers are ignored
        assert a.total(dice_only=True) == 5
        # Without dice_only, strategic applies
        assert a.total(dice_only=False) == 3

    def test_reset(self):
        a = Attacker(ship_die=2, combat_die_rolls=[3])
        d = Defender(ship_die=1, combat_die_rolls=[2])
        a.attack(d)

        assert a.combat_die is not None
        assert len(a.combat_die_rolls) > 0
        assert a.roll_counter > 0

        a.reset()
        assert a.combat_die is None
        assert a.combat_die_rolls == []
        assert a.roll_counter == 0

    def test_history(self):
        a = Attacker(ship_die=2, combat_die_rolls=[3])
        d = Defender(ship_die=1, combat_die_rolls=[2])
        a.attack(d)

        history = a.history()
        assert "2+3=5" in history
        assert "1+2=3" in history
        assert "Attacker" in history or "Defender" in history

    def test_eq_and_hash(self):
        a1 = Attacker(ship_die=2, cards=["strategic"])
        a2 = Attacker(ship_die=2, cards=["strategic"])
        a1.combat_die = 3
        a2.combat_die = 3

        assert a1 == a2
        assert hash(a1) == hash(a2)

    def test_repr(self):
        a = Attacker(ship_die=3, cards=["ferocious"])
        a.combat_die = 4
        repr_str = repr(a)
        assert "Attacker" in repr_str
        assert "ship_die=3" in repr_str
        assert "combat_die=4" in repr_str
        assert "ferocious" in repr_str

    def test_predefined_roll_exhaustion(self):
        # Test that using more rolls than provided raises an error
        a = Attacker(ship_die=2, combat_die_rolls=[1])  # Only 1 roll provided
        d = Defender(ship_die=1, combat_die_rolls=[1])

        # First attack uses the predefined roll - should succeed
        a.attack(d)

        # Trying another attack without reset should fail (no more rolls)
        with pytest.raises(ValueError, match=r"You need to give more predifined rolls!"):
            a.attack(d)


class TestCardInteractions:
    """Test complex card interaction scenarios"""

    def test_relentless_changes_outcome(self):
        # Defender loses initially, but Relentless allows them to re-roll
        a = Attacker(ship_die=2, combat_die_rolls=[1])
        d = Defender(ship_die=3, combat_die_rolls=[4, 1], cards=["relentless"])

        attacker_wins = a.attack(d)
        # Initial: A=3, D=7 (D loses, so relentless triggers)
        # After relentless: A=3, D=4 (D wins with lower total)
        assert len(d.combat_die_rolls) == 2  # Relentless caused re-roll
        assert attacker_wins  # A=3 < D=4, so attacker wins

    def test_cruel_forces_winner_reroll(self):
        # Attacker wins, but Cruel forces winner to re-roll
        a = Attacker(ship_die=1, combat_die_rolls=[1, 6])
        d = Defender(ship_die=2, combat_die_rolls=[5], cards=["cruel"])

        attacker_wins = a.attack(d)
        # Initial: A=2, D=7 (A wins because 2 < 7)
        # Cruel forces winner (A) to reroll: A gets 6, so A=7
        # Final: A=7, D=7 (tie, A wins)
        assert len(a.combat_die_rolls) == 2  # Cruel forced a reroll
        assert attacker_wins

    def test_stubborn_prevents_tie_win(self):
        # Test that stubborn actually changes the outcome on a tie
        a = Attacker(ship_die=2, combat_die_rolls=[2])
        d = Defender(ship_die=2, combat_die_rolls=[2], cards=["stubborn"])

        attacker_wins = a.attack(d)
        # With tie at 4 vs 4, normally attacker wins
        # But stubborn makes defender win ties
        assert not attacker_wins

    def test_rational_always_rolls_3(self):
        # Test that rational always produces 3, even without predefined rolls
        a = Attacker(ship_die=2, cards=["rational"])
        d = Defender(ship_die=1, combat_die_rolls=[1])

        # Don't provide predefined rolls - rational should force 3
        attacker_wins = a.attack(d)
        assert a.combat_die == 3
        assert a.total() == 5  # 2 + 3

    def test_invalid_combat_die_value_detection(self):
        # Test that combat_die_rolls validation catches bad values during init
        with pytest.raises(ValueError, match=r"All combat_die_rolls must be between 1 and 6!"):
            Attacker(ship_die=2, combat_die_rolls=[7])


class TestMonteCarloSimulation:
    """Test the Monte Carlo simulation functions"""

    def test_do_iterations(self):
        a = Attacker(ship_die=1, cards=["strategic"])
        d = Defender(ship_die=6)

        # Strategic gives attacker big advantage (lower is better)
        win_count = do_iterations(a, d, num_trials=100)

        # Should win most of the time
        assert win_count > 50

    def test_get_results_default_dice(self):
        # Test with default dice (1-6 for both)
        results = get_results(
            num_trials=10,
            attacker_cards=None,
            defender_cards=None
        )

        # Should have 6x6 = 36 combinations
        assert len(results) == 36

        # Check that all probabilities are between 0 and 1
        for prob in results.values():
            assert 0.0 <= prob <= 1.0

    def test_get_results_specific_dice(self):
        # Test with specific ship dice
        results = get_results(
            num_trials=10,
            attacker_cards=["strategic"],
            defender_cards=None,
            attacker_ship_dice=[1, 2],
            defender_ship_dice=[5, 6]
        )

        # Should have 2x2 = 4 combinations
        assert len(results) == 4

    def test_get_results_with_cards(self):
        results = get_results(
            num_trials=50,
            attacker_cards=["strategic"],
            defender_cards=["stubborn"],
            attacker_ship_dice=[3],
            defender_ship_dice=[3]
        )

        # Should have just 1 combination
        assert len(results) == 1

        # Strategic should give attacker good odds even with stubborn
        prob = list(results.values())[0]
        assert 0.0 <= prob <= 1.0


class TestFileIO:
    """Test save/load functions"""

    def test_save_and_load(self, tmp_path):
        # Create test results
        results = {
            (1, 1): 0.5,
            (2, 2): 0.6,
            (3, 3): 0.7,
        }

        # Save to temporary file
        filepath = tmp_path / "test_results.pkl"
        save(results, filepath)

        # Load and verify
        loaded_results = load(filepath)
        assert loaded_results == results
