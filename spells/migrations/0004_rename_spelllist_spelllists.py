# Generated by Django 5.2 on 2025-05-28 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spells', '0003_spelllist_remove_spell_spelllist_spell_spelllist'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpellList',
            new_name='SpellLists',
        ),
    ]
