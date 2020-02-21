import pytest

from quantum import Attacker, Defender


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
        with pytest.raises(ValueError, match="ship_die must be between 1 and 6!*"):
            a = Attacker(ship_die=7, combat_die_rolls=[1])
        with pytest.raises(ValueError, match="ship_die must be between 1 and 6!*"):
            a = Attacker(ship_die=0, combat_die_rolls=[1])

    def test_invalid_combat_die(self):
        with pytest.raises(
            ValueError, match="All combat_die_rolls must be between 1 and 6!*"
        ):
            a = Attacker(ship_die=6, combat_die_rolls=[7])
        with pytest.raises(
            ValueError, match="All combat_die_rolls must be between 1 and 6!*"
        ):
            a = Attacker(ship_die=6, combat_die_rolls=[0])


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
        a = Attacker(ship_die=2, combat_die_rolls=[4, 5], cards=["relentless"],)
        d = Defender(ship_die=1, combat_die_rolls=[2])

        assert a.cards == ("relentless",)
        attacker_wins = a.attack(d)
        assert a.total() == 7
        assert d.total() == 3
        assert not attacker_wins

    def test_scrappy_attacker(self):
        a = Attacker(ship_die=2, combat_die_rolls=[4, 5], cards=["scrappy"],)
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
