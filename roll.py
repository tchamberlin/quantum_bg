# Let's say we have a situation where we are trying to roll a specific value during reconfigure?
# What is the probability of getting it? It's not simply 1/6!

import argparse
import logging
import random

ROLLS = None
# ROLLS = iter((6, 4))

logger = logging.getLogger(__name__)


def roll(debug=True):
    return random.randint(1, 6)


def _reconfigure(current_ship_die):
    """Return a random roll that is not equal to the current one"""
    if ROLLS is not None:
        try:
            roll = next(ROLLS)
        except StopIteration:
            print("Reached end of pre-defined rolls; random from here on out!")
        else:
            print(f"Manually rolled {roll}")
            return roll
    return random.choice([value for value in range(1, 7) if value != current_ship_die])


def reconfigure(
    current_ship_die, desired_ship_die, ship_abilities_remaining, actions_remaining
):
    new_ship_die = current_ship_die

    logger.debug(
        "!",
        current_ship_die,
        desired_ship_die,
        ship_abilities_remaining,
        actions_remaining,
    )
    if ship_abilities_remaining == actions_remaining == 0:
        logger.debug("Done!")
        return current_ship_die, ship_abilities_remaining, actions_remaining

    if ship_abilities_remaining > 0 and current_ship_die == 6:
        logger.debug(
            f"RECONFIGURE: We might be able to get to our target by free reconfigure!"
        )
        new_ship_die, ship_abilities_remaining = (
            _reconfigure(current_ship_die),
            ship_abilities_remaining - 1,
        )
        logger.debug(f"Reconfigured from {current_ship_die} to {new_ship_die}")

    elif (
        ship_abilities_remaining > 0
        and current_ship_die == 4
        and desired_ship_die in [3, 5]
    ):
        logger.debug(f"MODIFY: We can get to our target by modifying!")
        new_ship_die = desired_ship_die
        logger.debug(f"Modified from {current_ship_die} to {desired_ship_die}")
        ship_abilities_remaining -= 1
    elif actions_remaining:
        logger.debug("RAW RECONF: yep")
        new_ship_die, actions_remaining = (
            _reconfigure(current_ship_die),
            actions_remaining - 1,
        )
        logger.debug(f"RAW: Reconfigured from {current_ship_die} to {new_ship_die}")

    # elif not actions_remaining:
    #     logger.debug("Out of actions :(")
    # else:
    #     raise AssertionError("wut")

    logger.debug(f"Abilities remaining: {ship_abilities_remaining}")
    logger.debug(f"Actions remaining: {actions_remaining}")

    if (
        actions_remaining or (new_ship_die == 6 and ship_abilities_remaining)
    ) and new_ship_die != desired_ship_die:
        return reconfigure(
            new_ship_die, desired_ship_die, ship_abilities_remaining, actions_remaining,
        )

    return (
        new_ship_die,
        actions_remaining,
        ship_abilities_remaining,
    )


def main():
    args = parse_args()
    if args.verbose:
        init_logging(logging.DEBUG)
    else:
        init_logging(logging.INFO)
    current_ship_die = args.ship_die
    desired_ship_die = args.desired_ship_die

    num_success = 0
    for i in range(args.num_trials):
        result, actions_remaining, ship_abilities_remaining = full_reconfigure(
            current_ship_die=current_ship_die,
            desired_ship_die=desired_ship_die,
            ship_abilities_remaining=args.abilities,
            actions_remaining=args.actions,
        )
        if result:
            num_success += 1
        # print(result)

    res = num_success / args.num_trials
    print(f"{num_success=} / {args.num_trials=} = {res:.2%}")


def full_reconfigure(
    current_ship_die, desired_ship_die, ship_abilities_remaining, actions_remaining
):
    if current_ship_die == desired_ship_die:
        print("Current and desired ship die values are the same!")
        return True, desired_ship_die, ship_abilities_remaining

    new_ship_die, actions_remaining, ship_abilities_remaining = reconfigure(
        current_ship_die, desired_ship_die, ship_abilities_remaining, actions_remaining
    )

    return new_ship_die == desired_ship_die, actions_remaining, ship_abilities_remaining


def check_die(parser, value):
    if not (1 <= value <= 6):
        parser.error("Die must be 1-6!")


def check_positive(parser, value):
    if value and value <= 0:
        parser.error("Number must be >0")


def check_positive_allow_zero(parser, value):
    if value and value < 0:
        parser.error("Number must be >=0")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ship_die", type=int)
    parser.add_argument("desired_ship_die", type=int)
    parser.add_argument("-a", "--abilities", type=int, default=1)
    parser.add_argument("-A", "--actions", type=int, default=3)
    parser.add_argument("-n", "--num-trials", type=int, default=10000)
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    check_die(parser, args.ship_die)
    check_die(parser, args.desired_ship_die)
    check_positive(parser, args.abilities)
    check_positive(parser, args.actions)
    check_positive_allow_zero(parser, args.num_trials)
    return args


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
