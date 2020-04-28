import dask

from tqdm import tqdm

from django.db.models import Q, Count

from quantum_nologs import do_iterations, Attacker, Defender, CARDS
from rolls.models import Card, Hand, Encounter

ATTACKER_ADVANTAGES = range(1 - 6, 6 - 1 + 1)
UNIQUE_ENCOUNTERS = tuple(
    (1, 1 - d) if d < 0 else (1 + d, 1) for d in ATTACKER_ADVANTAGES
)


def get_hand(card_names):
    cards = Card.objects.filter(name__in=card_names)
    q = Q()
    for card in cards:
        q &= Q(cards=card)

    tqdm.write(f"{card_names=}")
    return (
        Hand.objects.annotate(num_cards=Count("cards"))
        .filter(num_cards=cards.count())
        .get(q)
    )

def handle_all_encounters_parallel(num_trials=1000):
    execs = []

    for attacker_hand in tqdm(Hand.objects.all()):
        result = dask.delayed(handle_attacker_hand)(
            attacker_hand=attacker_hand, num_trials=num_trials, do_create=True
        )
        execs.append(result)

    all_results = dask.compute(*execs)

def handle_all_encounters(num_trials=1000):
    all_encounters_to_create = []

    for attacker_hand in tqdm(Hand.objects.all()):
        all_encounters_to_create.extend(
            handle_attacker_hand(attacker_hand=attacker_hand, num_trials=num_trials,)
        )

    return all_encounters_to_create


def handle_attacker_hand(attacker_hand, num_trials=1000, do_create=False):
    encounters_to_create = []
    tqdm.write(f"{attacker_hand=}")
    possible_defender_hands = Hand.objects.all()
    for card in attacker_hand.cards.all():
        possible_defender_hands = possible_defender_hands.exclude(cards=card)

    tqdm.write(f"{possible_defender_hands.count()=}")
    for defender_hand in possible_defender_hands:
        _encounters_to_create = handle_encounters_between_hands(
            attacker_hand, defender_hand, num_trials=num_trials
        )
        encounters_to_create.extend(_encounters_to_create)

    if do_create:
        Encounter.objects.bulk_create(encounters_to_create)
    return encounters_to_create


def handle_encounters_between_hands(
    attacker_hand, defender_hand, num_trials=1000, encounters=UNIQUE_ENCOUNTERS,
):
    encounters_to_create = []
    for attacker_ship_die, defender_ship_die in encounters:
        _attacker = Attacker(
            ship_die=attacker_ship_die,
            cards=attacker_hand.cards.values_list("name", flat=True),
        )
        _defender = Defender(
            ship_die=defender_ship_die,
            cards=defender_hand.cards.values_list("name", flat=True),
        )
        attacker_win_count = do_iterations(_attacker, _defender, num_trials)
        attacker_win_ratio = attacker_win_count / num_trials
        encounter = Encounter(
            attacker_advantage=attacker_ship_die - defender_ship_die,
            attacker_hand=attacker_hand,
            defender_hand=defender_hand,
            attacker_win_ratio=attacker_win_ratio,
            num_trials=num_trials
        )
        encounters_to_create.append(encounter)

    return encounters_to_create
