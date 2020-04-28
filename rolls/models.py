from django.db import models

from rolls.managers import HandManager


class Card(models.Model):
    """Represents a single unique Advance Card"""

    name = models.CharField(max_length=32)
    # display = models.CharField(max_length=32)
    description = models.TextField()

    def __str__(self):
        return self.name


class Hand(models.Model):
    """Represents a single unique "hand" of Command Cards"""

    cards = models.ManyToManyField(Card)

    slug = models.CharField(max_length=128)

    objects = HandManager()

    def __str__(self):
        if self.cards.exists():
            return f"{', '.join(self.cards.values_list('name', flat=True))}"

        return "No Cards"


class Encounter(models.Model):
    """Represents a single unique combat encounter"""

    attacker_advantage = models.IntegerField(
        help_text="The difference in ship die value between the attacker and "
        "defender (i.e. attacker - defender)"
    )
    attacker_hand = models.ForeignKey(
        Hand, on_delete=models.CASCADE, related_name="encounters_as_attacker"
    )
    defender_hand = models.ForeignKey(
        Hand, on_delete=models.CASCADE, related_name="encounters_as_defender"
    )
    attacker_win_ratio = models.FloatField()
    num_trials = models.IntegerField(
        help_text="Number of trials over which attacker_win_ratio was calculated"
    )
    # TODO: constraint that prevents overlapping cards between
    #       attacker and defender?

    def __str__(self):
        return (
            f"Attacker ({self.attacker_hand}) vs. Defender "
            f"({self.defender_hand}) [adv. {self.attacker_advantage:+}]: "
            f"{self.attacker_win_ratio:.2%}"
        )

    def compare_to_empty_hand(self):
        """Compare this Encounter to the same Encounter without any cards"""
        
        empty_hand = Hand.objects.get(cards=None)
        to = Encounter.objects.get(
            attacker_advantage=self.attacker_advantage,
            attacker_hand=empty_hand,
            defender_hand=empty_hand,
        )

        return f"{self} <vs. {to.attacker_win_ratio:.2%} without cards>"

    def compare_to_base(self):
        """Compare this Encounter to a 0-advantage Encounter without any cards"""

        empty_hand = Hand.objects.get(cards=None)
        base = Encounter.objects.get(
            attacker_advantage=0,
            attacker_hand=empty_hand,
            defender_hand=empty_hand,
        )

        return f"{self} <vs. {base.attacker_win_ratio:.2%} base matchup>"

    def to_string(self, attacker_ship_die, defender_ship_die):
        return (
            f"Attacker {attacker_ship_die} ({self.attacker_hand}) will win vs. "
            f"Defender {defender_ship_die} ({self.defender_hand}) "
            f"{self.attacker_win_ratio:.2%} of the time [adv. {self.attacker_advantage:+}]"
        )
