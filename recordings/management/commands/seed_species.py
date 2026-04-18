"""
recordings/management/commands/seed_species.py

Run with:
    python manage.py seed_species

Populates the database with 20 real Northern Territory species.
Safe to run multiple times — uses get_or_create() so no duplicates.
"""

from django.core.management.base import BaseCommand
from recordings.models import Species, ConservationStatus


SPECIES_DATA = [
    {
        'common_name': 'Black-footed Rock Wallaby',
        'scientific_name': 'Petrogale lateralis',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A small wallaby found in rocky outcrops across central and western Australia.',
    },
    {
        'common_name': 'Northern Quoll',
        'scientific_name': 'Dasyurus hallucatus',
        'conservation_status': ConservationStatus.ENDANGERED,
        'is_native': True,
        'not_native': False,
        'description': 'A carnivorous marsupial endemic to northern Australia, threatened by cane toads and habitat loss.',
    },
    {
        'common_name': 'Gouldian Finch',
        'scientific_name': 'Erythrura gouldiae',
        'conservation_status': ConservationStatus.ENDANGERED,
        'is_native': True,
        'not_native': False,
        'description': 'A brightly coloured finch found in tropical savanna woodlands of northern Australia.',
    },
    {
        'common_name': 'Brush-tailed Rabbit-rat',
        'scientific_name': 'Conilurus penicillatus',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A native rodent found in monsoon forests and adjacent woodlands of the NT.',
    },
    {
        'common_name': 'Flatback Sea Turtle',
        'scientific_name': 'Natator depressus',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'Endemic to the Australian continental shelf, nesting on beaches across northern Australia.',
    },
    {
        'common_name': 'Partridge Pigeon',
        'scientific_name': 'Geophaps smithii',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A ground-dwelling pigeon found in tropical savanna woodlands of northern Australia.',
    },
    {
        'common_name': 'Masked Owl',
        'scientific_name': 'Tyto novaehollandiae kimberli',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A large owl found in forests and woodlands across northern Australia.',
    },
    {
        'common_name': 'Ghost Bat',
        'scientific_name': 'Macroderma gigas',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'Australia\'s only carnivorous bat, roosting in caves and mine shafts across the NT.',
    },
    {
        'common_name': 'Freshwater Sawfish',
        'scientific_name': 'Pristis pristis',
        'conservation_status': ConservationStatus.CRITICALLY_ENDANGERED,
        'is_native': True,
        'not_native': False,
        'description': 'A large elasmobranch found in rivers and coastal waters of northern Australia.',
    },
    {
        'common_name': 'NT Thick-tailed Gecko',
        'scientific_name': 'Underwoodisaurus milii',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'A robust gecko found in rocky areas and woodlands across central Australia.',
    },
    {
        'common_name': 'Arnhem Land Rock Rat',
        'scientific_name': 'Zyzomys maini',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A native rodent restricted to rocky sandstone escarpments of Arnhem Land.',
    },
    {
        'common_name': 'Sandstone Sheathtail Bat',
        'scientific_name': 'Taphozous jobensis',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'A bat species found roosting in sandstone caves and escarpments across northern Australia.',
    },
    {
        'common_name': 'Blue-winged Kookaburra',
        'scientific_name': 'Dacelo leachii',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'A large kingfisher found in open woodlands and savanna across northern Australia.',
    },
    {
        'common_name': 'Olive Python',
        'scientific_name': 'Liasis olivaceus',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'One of Australia\'s largest snakes, found near water in rocky gorges of the NT.',
    },
    {
        'common_name': 'Red Goshawk',
        'scientific_name': 'Erythrotriorchis radiatus',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'Australia\'s rarest raptor, found in tall open forest and woodland of northern Australia.',
    },
    {
        'common_name': 'Saltwater Crocodile',
        'scientific_name': 'Crocodylus porosus',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'The world\'s largest living reptile, found in rivers, estuaries, and coastal waters of the NT.',
    },
    {
        'common_name': 'Northern Brown Bandicoot',
        'scientific_name': 'Isoodon macrourus',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'A medium-sized bandicoot found in grassy woodlands and scrublands of northern Australia.',
    },
    {
        'common_name': 'Purple-crowned Fairy-wren',
        'scientific_name': 'Malurus coronatus',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A small bird restricted to dense riparian vegetation along rivers of northern Australia.',
    },
    {
        'common_name': 'Pig-nosed Turtle',
        'scientific_name': 'Carettochelys insculpta',
        'conservation_status': ConservationStatus.VULNERABLE,
        'is_native': True,
        'not_native': False,
        'description': 'A unique freshwater turtle found in rivers and lagoons of the NT and southern New Guinea.',
    },
    {
        'common_name': 'Cane Toad',
        'scientific_name': 'Rhinella marina',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': False,
        'not_native': True,
        'description': 'An invasive species introduced to Australia in 1935, now widespread across northern Australia and a major threat to native wildlife.',
    },
    {
        'common_name': 'Mertens Water Monitor',
        'scientific_name': 'Varanus mertensi',
        'conservation_status': ConservationStatus.LEAST_CONCERN,
        'is_native': True,
        'not_native': False,
        'description': 'A semi-aquatic monitor lizard found along rivers and billabongs across northern Australia.',
    },
    {
        'common_name': 'Arnhem Rock Rat',
        'scientific_name': 'Zyzomys arnhemensis',
        'conservation_status': ConservationStatus.NEAR_THREATENED,
        'is_native': True,
        'not_native': False,
        'description': 'A native rodent endemic to the rocky escarpments of Arnhem Land in the NT.',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with 22 Northern Territory species'

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        for data in SPECIES_DATA:
            obj, created = Species.objects.get_or_create(
                scientific_name=data['scientific_name'],
                defaults={
                    'common_name':          data['common_name'],
                    'conservation_status':  data['conservation_status'],
                    'is_native':            data['is_native'],
                    'not_native':           data['not_native'],
                    'description':          data['description'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {obj.common_name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Already exists: {obj.common_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone — {created_count} created, {updated_count} already existed.'
            )
        )