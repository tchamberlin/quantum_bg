import argparse
from functools import reduce
import operator

from django.core.management.base import BaseCommand

from rolls.models import Card, Encounter, Hand
from qq import prob_of_win2


def prob_of_win_all(probabilities):
    return reduce(operator.mul, probabilities)


def die_face(die):
    value = int(die)
    if not 1 <= value <= 6:
        raise ValueError("Die faces must be between 1 and 6")
    return value


def parse_fights(fights_str):
    return [[die_face(die) for die in fs.split(":")] for fs in fights_str]


def battle_summary(fights, attacker_cards, defender_cards, win_condition):
    substr = "ALL fights" if win_condition == "all" else "ANY fight"
    print(f"Attacker must win {substr} to win battle")
    print(f"Engagement Summary:")
    for fight_num, fight in enumerate(fights, 1):
        attacker_ship_die, defender_ship_die, attacker_win_ratio = fight
        print(
            f"  Fight {fight_num}: "
            f"{attacker_ship_die} ({', '.join(attacker_cards) if attacker_cards else 'No Cards'}) "
            "attacks "
            f"{defender_ship_die} ({', '.join(defender_cards) if defender_cards else 'No Cards'}) "
            f"[probability of win: {attacker_win_ratio:.2%}]"
        )


def check_hands(attacker_cards, defender_cards):
    if attacker_cards and defender_cards:
        shared = set(attacker_cards).intersection(set(defender_cards))
        if shared:
            raise ValueError(
                f"Attacker and defender cannot have the same card! Shared cards: {shared}"
            )


class Command(BaseCommand):
    def add_arguments(self, parser):
        card_names = Card.objects.values_list("name", flat=True)
        parser.add_argument(
            "fights",
            metavar="attacker:defender",
            nargs="+",
            help="One or more 'fight' strings. Format is 'attacker:defender' "
            "(e.g. 1:2 3:2)",
        )
        parser.add_argument(
            "-a",
            "--attacker-cards",
            nargs="+",
            type=lambda x: x.lower(),
            choices=card_names,
        )
        parser.add_argument(
            "-d",
            "--defender-cards",
            nargs="+",
            type=lambda x: x.lower(),
            choices=card_names,
        )
        parser.add_argument(
            "-w", "--win-condition", choices=["all", "any"], default="any"
        )

    def handle(self, *args, **options):
        check_hands(options["attacker_cards"], options["defender_cards"])
        
        attacker_hand = Hand.objects.get_by_cards(options["attacker_cards"])
        defender_hand = Hand.objects.get_by_cards(options["defender_cards"])

        fights = parse_fights(options["fights"])
        fights_with_ratios = []
        for attacker_ship_die, defender_ship_die in fights:
            attacker_advantage = attacker_ship_die - defender_ship_die

            encounter = Encounter.objects.get(
                attacker_advantage=attacker_advantage,
                attacker_hand=attacker_hand,
                defender_hand=defender_hand,
            )
            fights_with_ratios.append(
                (attacker_ship_die, defender_ship_die, encounter.attacker_win_ratio)
            )

        battle_summary(
            fights_with_ratios,
            options["attacker_cards"],
            options["defender_cards"],
            options["win_condition"],
        )

        if options["win_condition"] == "any":
            win_cond_str = "at least 1 engagement"
            prob_of_win = prob_of_win2([fwr[2] for fwr in fights_with_ratios])
        elif options["win_condition"] == "all":
            win_cond_str = "all engagements"
            prob_of_win = prob_of_win_all([fwr[2] for fwr in fights_with_ratios])
        else:
            raise ValueError(f"Invalid win_condition: {options['win_condition']}")

        print(f"{prob_of_win:.2%} chance that attacker wins {win_cond_str}")
