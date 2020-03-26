"""Take interval-based images from a webcam"""

from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint
import argparse
import logging
import math
import operator
import pickle
import random
import subprocess


# logger = logging.getLogger(__name__)

CARDS = [
    "ferocious",
    "relentless",
    "cruel",
    "scrappy",
    "strategic",
    "rational",
    "stubborn",
]


def load(path):
    with open(path, "rb") as file:
        results = pickle.load(file)

    return results


def save(results, path):
    with open(path, "wb") as file:
        pickle.dump(results, file, protocol=5)


class Side:
    def __init__(self, ship_die, cards=None, combat_die_rolls=None):
        if not (1 <= ship_die <= 6):
            raise ValueError(f"ship_die must be between 1 and 6! Got: {ship_die}")

        self.ship_die = ship_die
        self.combat_die = None

        if cards:
            invalid_cards = [card for card in cards if card not in CARDS]
            if invalid_cards:
                raise ValueError(f"Invalid cards: {invalid_cards}")

            self.cards = tuple(cards)
        else:
            self.cards = tuple()

        self.predefined_combat_die_rolls = (
            combat_die_rolls if combat_die_rolls is not None else []
        )
        self.combat_die_rolls = []
        for combat_die in self.predefined_combat_die_rolls:
            if not (1 <= combat_die <= 6):
                raise ValueError(
                    f"All combat_die_rolls must be between 1 and 6! Got: {combat_die}"
                )

        self.roll_counter = 0
        self.combat_log = []

    def __repr__(self):
        return f"{self.__class__.__name__}(ship_die={self.ship_die}, combat_die={self.combat_die}, cards={self.cards})"

    @classmethod
    def to_string(cls, ship_die, combat_die, cards):
        if combat_die:
            string = f"{ship_die}+{combat_die}={ship_die+ combat_die}"
        else:
            string = f"{ship_die}"

        if cards:
            string = f"{string} [{', '.join(cards)}]"
        return f"{cls.__name__} {string}"

    def __str__(self):
        return self.to_string(self.ship_die, self.combat_die, self.cards)

    def __eq__(self, die):
        return hash(self) == hash(die)

    def __hash__(self):
        return hash((self.ship_die, self.cards, self.combat_die))

    def roll(self):
        if "rational" in self.cards:
            the_roll = 3

        elif self.predefined_combat_die_rolls:
            the_roll = self.predefined_combat_die_rolls[self.roll_counter]
        else:
            the_roll = random.randint(1, 6)

        self.combat_die = the_roll
        self.combat_die_rolls.append(the_roll)
        self.roll_counter += 1

        if not (1 <= the_roll <= 6):
            raise ValueError(f"Combat die must be between 1 and 6! Got: {the_roll}")

    def total(self, dice_only=False):
        total = self.ship_die + self.combat_die
        if dice_only:
            return total

        if "ferocious" in self.cards:
            total -= 1

        if "strategic" in self.cards:
            total -= 2

        return total

    def reset(self):
        self.combat_die = None
        self.roll_counter = 0
        self.combat_die_rolls = []

    def history(self):
        history = []
        for attacker, defender, attacker_wins in self.combat_log:
            attacker_ship_die, attacker_combat_die, attacker_total = attacker
            defender_ship_die, defender_combat_die, defender_total = defender
            vstring = "Attacker" if attacker_wins else "Defender"
            history.append(
                f"{attacker_ship_die}+{attacker_combat_die}={attacker_total} vs. "
                f"{defender_ship_die}+{defender_combat_die}={defender_total}: {vstring}"
            )

        return "\n".join(history)


class Attacker(Side):
    def recalc(self, attacker, defender, comparator=operator.le):
        attacker_total = attacker.total()
        defender_total = defender.total()
        attacker_wins = comparator(attacker_total, defender_total)
        winner, loser = (attacker, defender) if attacker_wins else (defender, attacker)

        self.combat_log.append(
            (
                (attacker.ship_die, attacker.combat_die, attacker.total()),
                (defender.ship_die, defender.combat_die, defender.total()),
                attacker == winner,
            )
        )
        return winner, loser

    def attack(self, defender):
        attacker = self

        attacker.roll()
        defender.roll()
        winner, loser = self.recalc(attacker, defender)

        # If the LOSER holds Relentless, they can re-roll
        # We assume that the loser will ALWAYS do this, and that the winner
        # NEVER will
        if "relentless" in loser.cards:
            prev_winner = winner
            loser.roll()
            winner, loser = self.recalc(attacker, defender)

        # If the ATTACKER holds Scrappy, they can re-roll
        # We assume that, if they lose, they will ALWAYS do this, and that
        # they never will if they win
        if loser == attacker and "scrappy" in attacker.cards:
            prev_winner = winner
            loser.roll()
            winner, loser = self.recalc(attacker, defender)

        # If the LOSER holds Cruel, they can force the WINNER to re-roll
        # We assume that they will ALWAYS do this, and that the LOSER will
        # never do this
        if "cruel" in loser.cards:
            prev_winner = winner
            winner.roll()
            winner, loser = self.recalc(attacker, defender)

        # If the DEFENDER holds Stubborn, then they break ties
        if loser == defender and "stubborn" in defender.cards:
            prev_winner = winner
            # So, instead of the attacker winning if it is LESS THAN OR
            # EQUAL TO, it only wins if it is strictly LESS THAN the defender
            # total
            winner, loser = self.recalc(attacker, defender, comparator=operator.lt)

        if (
            attacker.predefined_combat_die_rolls
            and attacker.predefined_combat_die_rolls != attacker.combat_die_rolls
        ):
            raise AssertionError(
                "Attacker predefined_combat_die_rolls "
                f"{attacker.predefined_combat_die_rolls} don't match actual: "
                f"{attacker.combat_die_rolls}"
            )
        if (
            defender.predefined_combat_die_rolls
            and defender.predefined_combat_die_rolls != defender.combat_die_rolls
        ):
            raise AssertionError(
                "Defender predefined_combat_die_rolls "
                f"{defender.predefined_combat_die_rolls} don't match actual: "
                f"{defender.combat_die_rolls}"
            )
        return winner == attacker


class Defender(Side):
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--save", type=Path)
    parser.add_argument("-i", "--compare-to", type=Path)
    parser.add_argument("-a", "--attacker-cards", nargs="+", choices=CARDS)
    parser.add_argument(
        "-A", "--attackers", dest="attacker_ship_dice", nargs="+", type=int
    )
    parser.add_argument("-d", "--defender-cards", nargs="+", choices=CARDS)
    parser.add_argument(
        "-D", "--defenders", dest="defender_ship_dice", nargs="+", type=int
    )
    parser.add_argument(
        "--rolls",
        metavar="ATTACKER_SHIP ATTACKER_ROLL DEFENDER_SHIP DEFENDER_ROLL",
        nargs=4,
        type=int,
    )
    parser.add_argument("-n", "--num-trials", type=int, default=1000)

    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()


def init_logging(level):
    """Initialize logging"""
    logging.getLogger().setLevel(level)
    _logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))


def do_iterations(attacker, defender, num_trials):
    attacker_win_count = 0
    for __ in range(num_trials):
        attacker.reset()
        defender.reset()
        result = attacker.attack(defender)
        attacker_win_count += int(result)

    return attacker_win_count


def get_results(
    num_trials,
    attacker_cards=None,
    defender_cards=None,
    attacker_ship_dice=None,
    defender_ship_dice=None,
):

    if attacker_ship_dice:
        attacker_ship_dice = [*attacker_ship_dice]
    else:
        attacker_ship_dice = range(1, 7)

    if defender_ship_dice:
        defender_ship_dice = [*defender_ship_dice]
    else:
        defender_ship_dice = range(1, 7)

    attackers = [Attacker(ship_die=n, cards=attacker_cards) for n in attacker_ship_dice]
    defenders = [Defender(ship_die=n, cards=defender_cards) for n in defender_ship_dice]

    results = {}
    for attacker in attackers:
        for defender in defenders:
            attacker_win_count = do_iterations(attacker, defender, num_trials)
            attacker_win_ratio = attacker_win_count / num_trials
            results[(attacker, defender)] = attacker_win_ratio
    return results


def do_stats(args):
    if args.compare_to:
        with open(args.compare_to, "rb") as file:
            base_results = pickle.load(file)
    else:
        base_results = None

    results = get_results(
        args.num_trials,
        attacker_cards=args.attacker_cards,
        defender_cards=args.defender_cards,
        attacker_ship_dice=args.attacker_ship_dice,
        defender_ship_dice=args.defender_ship_dice,
    )

    for key, attacker_win_ratio in results.items():
        attacker, defender = key
        if base_results:
            attacker_win_ratio_base = base_results[
                (attacker.ship_die, defender.ship_die)
            ]
            # diff_from_base = attacker_win_ratio - attacker_win_ratio_base
            diff_from_base = (
                attacker_win_ratio - attacker_win_ratio_base
            ) / attacker_win_ratio_base
            compare_str = (
                f" (vs. {attacker_win_ratio_base:.2%}; {diff_from_base:.2%} "
                "diff from base)"
            )
        else:
            compare_str = ""

        attacker.reset()
        defender.reset()
        print(
            f"<{attacker}> wins against <{defender}> "
            f"{attacker_win_ratio:.2%} of the time (over {args.num_trials} trials){compare_str}"
        )

    if args.save:
        with open(args.save, "wb") as file:
            results = {
                (key[0].ship_die, key[1].ship_die): value
                for key, value in results.items()
            }
            pickle.dump(results, file)


def do_specific(args):
    (
        attacker_ship_die,
        attacker_combat_die,
        defender_ship_die,
        defender_combat_die,
    ) = args.rolls
    attacker = Attacker(
        ship_die=attacker_ship_die,
        combat_die=attacker_combat_die,
        cards=args.attacker_cards,
    )
    defender = Defender(
        ship_die=defender_ship_die,
        combat_die=defender_combat_die,
        cards=args.defender_cards,
    )

    res = attacker.attack(defender)
    print(f"Winner: {attacker if res else defender}")


def main():
    args = parse_args()
    if args.verbose:
        init_logging(logging.DEBUG)
    else:
        init_logging(logging.INFO)

    if args.attacker_cards and args.defender_cards:
        shared = set(args.attacker_cards).intersection(set(args.defender_cards))
        if shared:
            raise ValueError(
                f"Attacker and defender cannot have the same card! Shared cards: {shared}"
            )
    results = {}

    if args.rolls:
        do_specific(args)
    else:
        do_stats(args)


if __name__ == "__main__":
    main()
