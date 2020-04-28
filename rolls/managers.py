from django.db.models import Manager, Count, Q


class HandManager(Manager):
    def get_by_cards(self, card_names):
        if not card_names:
            card_names = []

        slug = '|'.join(sorted(card_names))
        return self.get(slug=slug)
