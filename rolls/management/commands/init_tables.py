from tqdm import tqdm

from django.core.management.base import BaseCommand

from quantum_nologs import CARDS
from rolls.models import Card, Encounter, Hand
from table import get_possible_hands

def init_tables():
    for card_name in CARDS:
        Card.objects.create(name=card_name, description=card_name)

    possible_hands = get_possible_hands()
    for hand in tqdm(possible_hands):
        cards = Card.objects.filter(name__in=hand)
        assert cards.count() == len(hand)
        tqdm.write(f"{cards}=")
        hand = Hand.objects.create()
        hand.cards.set(cards)


class Command(BaseCommand):
    def handle(self, *args, **options):
        init_tables()
