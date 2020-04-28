import argparse

from django.core.management.base import BaseCommand

from rolls.models import Card, Encounter, Hand


def die_face(die):
    value = int(die)
    if not 1 <= value <= 6:
        raise ValueError()
    return value


class Command(BaseCommand):
    def add_arguments(self, parser):
        card_names = Card.objects.values_list("name", flat=True)
        parser.add_argument("attacker_ship_die", type=die_face)
        parser.add_argument("defender_ship_die", type=die_face)
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

    def handle(self, *args, **options):
        attacker_advantage = options["attacker_ship_die"] - options["defender_ship_die"]
        attacker_hand = Hand.objects.get_by_cards(options["attacker_cards"])
        defender_hand = Hand.objects.get_by_cards(options["defender_cards"])
        encounter = Encounter.objects.get(
            attacker_advantage=attacker_advantage,
            attacker_hand=attacker_hand,
            defender_hand=defender_hand,
        )
        print(f"{encounter.attacker_win_ratio}")
