from django.views.generic import ListView

from rolls.models import Encounter


class EncounterListView(ListView):
    model = Encounter
    template_name = 'rolls/encounter_list_view.html'
