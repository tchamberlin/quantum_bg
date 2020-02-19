"""Take interval-based images from a webcam"""

import argparse
from datetime import datetime, timedelta
import logging
import random
import math
import subprocess
from pathlib import Path
from pprint import pprint
import pickle

logger = logging.getLogger(__name__)

CARDS = [
    "ferocious",
    "relentless",
    "cruel",
    "scrappy",
    "strategic",
    "rational",
    "stubborn",
]


class Side:
    def __init__(self, ship_die, cards=None, combat_die=None):
        if not (1 <= ship_die <= 6):
            raise ValueError(f"ship_die must be between 1 and 6! Got: {ship_die}")

        if combat_die and not (1 <= combat_die <= 6):
            raise ValueError(f"combat_die must be between 1 and 6! Got: {combat_die}")

        self.ship_die = ship_die
        self.combat_die = combat_die

        if cards:
            invalid_cards = [card for card in cards if card not in CARDS]
            if invalid_cards:
                raise ValueError(f"Invalid cards: {invalid_cards}")

            self.cards = tuple(cards)
        else:
            self.cards = tuple()

    def __str__(self):
        if self.combat_die:
            string = (
                f"{self.ship_die}+{self.combat_die}={self.ship_die+ self.combat_die}"
            )
        else:
            string = f"{self.ship_die}"

        if self.cards:
            string = f"{string} [{', '.join(self.cards)}]"
        return string

    def __eq__(self, die):
        return hash(self) == hash(die)

    def __hash__(self):
        return hash((self.ship_die, self.cards, self.combat_die))

    def roll(self):
        self.combat_die = random.randint(1, 6)

    def total(self):
        if "rational" in self.cards:
            self.combat_die = 3

        total = self.ship_die + self.combat_die

        if "ferocious" in self.cards:
            logger.debug("Lowered effective roll by 1 due to Ferocious")
            total -= 1

        if "strategic" in self.cards:
            logger.debug("Lowered effective roll by 1 due to Strategic")
            total -= 2

        return total

    def reset(self):
        self.combat_die = None


class Attacker(Side):
    def attack(self, defender):
        attacker = self

        logger.debug(f"{attacker} attacking {defender}")
        attacker.roll()
        defender.roll()
        attacker_initial = attacker.total()
        defender_initial = defender.total()
        attacker_wins = attacker_initial <= defender_initial

        if attacker_wins:
            winner = attacker
            loser = defender
        else:
            winner = defender
            loser = attacker

        logger.debug(f"{attacker_initial=} vs. {defender_initial=}")

        # If the LOSER holds Relentless, they can re-roll
        # We assume that the loser will ALWAYS do this, and that the winner
        # NEVER will
        # This happens BEFORE Cruel!
        if "relentless" in loser.cards:
            prev_loser_str = str(loser)
            loser.roll()
            logger.debug(f"Loser {prev_loser_str} re-roll to {loser}")

            prev_winner = winner
            attacker_wins = attacker.total() <= defender.total()
            if attacker_wins:
                winner = attacker
                loser = defender
            else:
                winner = defender
                loser = attacker
            if prev_winner != winner:
                logger.debug("Upset due to Relentless!")

        if loser == attacker and "scrappy" in attacker.cards:
            prev_loser_str = str(loser)
            loser.roll()
            logger.debug(f"Loser {prev_loser_str} re-roll to {loser}")

            prev_winner = winner
            attacker_wins = attacker.total() <= defender.total()
            if attacker_wins:
                winner = attacker
                loser = defender
            else:
                winner = defender
                loser = attacker
            if prev_winner != winner:
                logger.debug("Upset due to Scrappy!")

        # If the LOSER holds Cruel, they can force the WINNER to re-roll
        # We assume that they will ALWAYS do this, and that the LOSER will
        # never do this
        if "cruel" in loser.cards:
            prev_winner_str = str(winner)
            winner.roll()
            logger.debug(f"Winner {prev_winner_str} re-roll to {winner}")

            prev_winner = winner
            attacker_wins = attacker.total() <= defender.total()
            if attacker_wins:
                winner = attacker
                loser = defender
            else:
                winner = defender
                loser = attacker
            if prev_winner != winner:
                logger.debug("Upset due to Relentless!")

        if loser == defender and "stubborn" in defender.cards:
            attacker_total = attacker.total()
            defender_total = defender.total()
            attacker_wins = attacker_total < defender_total
            prev_winner = winner
            if attacker_wins:
                winner = attacker
                loser = defender
            else:
                winner = defender
                loser = attacker
            if prev_winner != winner:
                logger.debug("Upset due to Stubborn!")

        return attacker_wins


class Defender(Side):
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--save", type=Path)
    parser.add_argument("-i", "--compare_to", type=Path)
    parser.add_argument("-a", "--attacker-cards", nargs="+", choices=CARDS)
    parser.add_argument(
        "-A", "--attackers", dest="attacker_ship_dice", nargs="+", type=int
    )
    parser.add_argument("-d", "--defender-cards", nargs="+", choices=CARDS)
    parser.add_argument(
        "-D", "--defenders", dest="defender_ship_dice", nargs="+", type=int
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
    _logger.addHandler(console_handler)
    _logger.setLevel(level)


def do_iterations(attacker, defender, num_trials):
    attacker_win_count = 0
    logger.debug("-" * 80)
    for __ in range(num_trials):
        attacker.reset()
        defender.reset()
        result = attacker.attack(defender)
        attacker_win_count += int(result)
        logger.debug("-" * 80)

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

    if args.compare_to:
        with open(args.compare_to, "rb") as file:
            logger.debug(f"Loaded base results from {args.compare_to.name}")
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
            f"Attacker <{attacker}> wins against defender "
            f"<{defender}> "
            f"{attacker_win_ratio:.2%} of the time (over {args.num_trials} trials){compare_str}"
        )

    if args.save:
        with open(args.save, "wb") as file:
            logger.debug(f"Wrote new results to {args.save.name}")
            results = {
                (key[0].ship_die, key[1].ship_die): value
                for key, value in results.items()
            }
            pickle.dump(results, file)


if __name__ == "__main__":
    main()
