from django.db.models import Manager, Count, Q

class HandManager(Manager):
    def get_by_cards(self, card_names):
        if not card_names:
            card_names = []
        q = Q()
        for card_name in card_names:
            q &= Q(cards__name=card_name)

        return (
            self.annotate(num_cards=Count("cards"))
            .filter(num_cards=len(card_names))
            .get(q)
        )
