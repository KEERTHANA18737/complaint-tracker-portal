"""
complaints/migrations/0002_seed_categories.py
Data migration – inserts the 5 default complaint categories so the
complaint submission form always has choices available, even on a
fresh install without loading fixtures.
"""

from django.db import migrations


CATEGORIES = [
    ('Roads & Transport',  'Potholes, damaged roads, traffic signals, footpaths', 'bi-signpost-2'),
    ('Water & Sanitation', 'Water supply, drainage, sewage, leakage issues',      'bi-droplet'),
    ('Electricity',        'Power outages, streetlights, illegal connections',     'bi-lightning-charge'),
    ('Waste Management',   'Garbage collection, illegal dumping, littering',       'bi-trash'),
    ('Public Safety',      'Street crime, unsafe structures, encroachments',       'bi-shield-exclamation'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('complaints', 'Category')
    for name, description, icon in CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={'description': description, 'icon': icon},
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('complaints', 'Category')
    names = [c[0] for c in CATEGORIES]
    Category.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]