import argparse
from collections import defaultdict
import itertools
import logging
import pickle
from pprint import pprint

from tqdm import tqdm

from quantum_nologs import do_iterations, Attacker, Defender, CARDS

logger = logging.getLogger(__name__)


def get_possible_hands(available_cards=CARDS):
    return [
        hand
        for num_attacker_cards in range(0, 4)
        for hand in itertools.permutations(available_cards, num_attacker_cards)
    ]


def load(path):
    with open(path, "rb") as file:
        tqdm.write(f"Read results from {path}")
        results = pickle.load(file)

    return results


def save(results, path):
    with open(path, "wb") as file:
        tqdm.write(f"Wrote new results to {path}")
        pickle.dump(results, file, protocol=5)


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
            results[(attacker.ship_die, defender.ship_die)] = attacker_win_ratio
    return results


def table(num_trials=1, output=None):
    possible_attacker_hands = get_possible_hands()

    results = defaultdict(dict)

    for attacker_hand in tqdm(possible_attacker_hands, unit="attacker_hand"):
        tqdm.write(f"{attacker_hand=}")
        possible_defender_cards = [c for c in CARDS if c not in attacker_hand]
        # tqdm.write(f"{possible_defender_cards=}")
        possible_defender_hands = get_possible_hands(possible_defender_cards)
        for defender_hand in tqdm(possible_defender_hands, unit="defender_hand"):
            # tqdm.write(f"{defender_hand=}")
            current = get_results(
                num_trials, attacker_cards=attacker_hand, defender_cards=defender_hand
            )
            # results[attacker_hand][defender_hand] = current
            results[attacker_hand][defender_hand] = current

        save(
            results[attacker_hand],
            f"attacker_{','.join(attacker_hand) if attacker_hand else 'empty'}.pkl",
        )


def main():
    args = parse_args()
    if args.verbose:
        init_logging(logging.DEBUG)
    else:
        init_logging(logging.INFO)

    if args.output:
        output = args.output
    else:
        output = f"all_results_{args.num_trials}_trials.pkl"
    table(args.num_trials, output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_trials", type=int, nargs="?", default=100)
    parser.add_argument("-o", "--output")
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
