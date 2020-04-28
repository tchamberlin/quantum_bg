import logging

import dask
from dask.distributed import Client, progress
from tqdm import tqdm

from django.db.models import Q, Count
from django.core.management.base import BaseCommand


from quantum_nologs import do_iterations, Attacker, Defender, CARDS
from rolls.models import Card, Encounter, Hand
from table import get_possible_hands
from rolls.utils import handle_all_encounters, handle_all_encounters_parallel

logger = logging.getLogger(__name__)




class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-n", "--num-trials", type=int, default=100)
        parser.add_argument("-p", "--parallel", action="store_true")

    def handle(self, *args, **options):
        if options["parallel"]:
            handle_all_encounters_parallel()
        else:
            all_encounters_to_create = handle_all_encounters(
                num_trials=options["num_trials"]
            )
            Encounter.objects.bulk_create(all_encounters_to_create)


    
