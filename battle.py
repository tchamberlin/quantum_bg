#! /usr/bin/env python

"""Determine likelihood of positive outcome in a given series of fights"""


import argparse
import logging

from quantum import CARDS, Attacker, Defender
from qq import qq

logger = logging.getLogger(__name__)


def do_fight(attacker_ship_die, defender_ship_die, attacker_cards, defender_cards):
    attacker = Attacker(
        ship_die=attacker_ship_die,
        # combat_die_rolls=[6],
        cards=attacker_cards,
    )
    defender = Defender(
        ship_die=defender_ship_die,
        # combat_die_rolls=[1],
        cards=defender_cards,
    )

    return attacker.attack(defender)


def do_battle_win_any(fights, attacker_cards, defender_cards):
    attacker_wins_battle = False
    attacker_wins_total = 0
    for attacker_ship_die, defender_ship_die in fights:
        attacker_wins = do_fight(
            attacker_ship_die, defender_ship_die, attacker_cards, defender_cards
        )
        if attacker_wins:
            attacker_wins_total += 1
            attacker_wins_battle = True

    return attacker_wins_battle, attacker_wins_total


def do_battle_win_all(fights, attacker_cards, defender_cards):
    attacker_wins_battle = True
    attacker_wins_total = 0
    for attacker_ship_die, defender_ship_die in fights:
        attacker_wins = do_fight(
            attacker_ship_die, defender_ship_die, attacker_cards, defender_cards
        )
        if attacker_wins:
            attacker_wins_total += 1
        else:
            attacker_wins_battle = False

    return attacker_wins_battle, attacker_wins_total


def do_battle(fights, attacker_cards, defender_cards, win_condition="all"):
    if win_condition == "all":
        return do_battle_win_all(fights, attacker_cards, defender_cards)

    if win_condition == "any":
        return do_battle_win_any(fights, attacker_cards, defender_cards)

    raise ValueError(f"win_condition must be 'all' or 'any'; got: {win_condition:!r}")


def battle_summary(fights, attacker_cards, defender_cards, win_condition):
    substr = "ALL fights" if win_condition == "all" else "ANY fight"
    print(f"Attacker must win {substr} to win battle")
    for fight_num, fight in enumerate(fights, 1):
        attacker_ship_die, defender_ship_die = fight
        prob = qq(
            attacker_ship_die=attacker_ship_die,
            defender_ship_die=defender_ship_die,
            attacker_cards=tuple(attacker_cards) if attacker_cards else (),
            defender_cards=tuple(defender_cards) if defender_cards else (),
        )
        print(
            f"Fight {fight_num}: "
            f"{attacker_ship_die} ({attacker_cards}) attacks "
            f"{defender_ship_die} ({defender_cards}) [probability: {prob}]"
        )


def main():
    args = parse_args()
    if args.verbose:
        init_logging(logging.DEBUG)
    else:
        init_logging(logging.INFO)
    # print(f"{args.fights=}")
    fights = parse_fights(args.fights)
    # print(f"{fights=}")
    battle_summary(fights, args.attacker_cards, args.defender_cards, args.win_condition)

    attacker_wins_battle_total = 0
    foo = {}
    for __ in range(args.num_trials):
        attacker_wins_battle, num_attacker_wins = do_battle(
            fights,
            args.attacker_cards,
            args.defender_cards,
            win_condition=args.win_condition,
        )
        if attacker_wins_battle:
            attacker_wins_battle_total += 1

        foo[num_attacker_wins] = num_attacker_wins
        # print(attacker_wins_battle)

    win_ratio = attacker_wins_battle_total / args.num_trials
    print(f"{attacker_wins_battle_total} / {args.num_trials} = {win_ratio:.2%}")
    print(foo)


# TODO: parse 1to6
def parse_fights(fights_str):
    return [[int(die) for die in fs.split(":")] for fs in fights_str]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("fights", nargs="+")
    parser.add_argument("-a", "--attacker-cards", nargs="+", choices=CARDS)
    parser.add_argument("-d", "--defender-cards", nargs="+", choices=CARDS)
    parser.add_argument("-n", "--num-trials", type=int, default=1000)
    parser.add_argument("-w", "--win-condition", choices=["all", "any"])
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()


def init_logging(level):
    """Initialize logging"""
    logging.getLogger().setLevel(level)
    _logger = logging.getLogger(__name__)
    # _logger = logging.getLogger("quantum")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(console_handler)
    _logger.setLevel(level)


if __name__ == "__main__":
    main()
