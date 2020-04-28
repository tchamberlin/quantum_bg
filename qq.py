"""Take interval-based images from a webcam"""

from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from pprint import pprint
import operator
import argparse
import logging
import math
import operator
import pickle
import random
import subprocess

from quantum import Attacker, Defender, CARDS
from table import load

logger = logging.getLogger(__name__)


def prob_of_win(p, n):
    return 1 - ((1 - p) ** n)


def prob_of_win2(probabilities):
    """Combine given probabilities to determine the overall probability of at least one win

    # trials is derived from length of probabilities"""

    return 1 - reduce(operator.mul, [1 - p for p in probabilities])


def qq(
    attacker_ship_die, defender_ship_die, attacker_cards, defender_cards, input_path=None
):
    if input_path is None:
        input_path = (
            f"attacker_{','.join(attacker_cards) if attacker_cards else 'empty'}.pkl"
        )
    results_for_attacker_cards = load(input_path)

    return results_for_attacker_cards[defender_cards][
        attacker_ship_die, defender_ship_die
    ]


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

    res = qq(
        args.input,
        args.attacker_ship_die,
        args.defender_ship_die,
        tuple(args.attacker_cards) if args.attacker_cards else (),
        tuple(args.defender_cards) if args.defender_cards else (),
    )
    attacker = Attacker(args.attacker_ship_die, args.attacker_cards)
    defender = Defender(args.defender_ship_die, args.defender_cards)
    if not args.trials or args.trials == 1:
        print(f"{attacker} vs. {defender}: {res:.2%}")
    else:
        print(
            f"{attacker} vs. {defender}: {res:.2%} "
            f"({prob_of_win(res, args.trials):.2%} over {args.trials} trials)"
        )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("attacker_ship_die", type=int)
    parser.add_argument("defender_ship_die", type=int)
    parser.add_argument("-i", "--input", default="./all_results.pkl", type=Path)
    parser.add_argument("-n", "--trials", type=int)
    parser.add_argument("-a", "--attacker-cards", nargs="+", choices=CARDS)
    parser.add_argument("-d", "--defender-cards", nargs="+", choices=CARDS)
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


if __name__ == "__main__":
    main()
