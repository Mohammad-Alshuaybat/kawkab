# Generated by Django 4.1 on 2023-02-03 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='tag',
            new_name='tags',
        ),
    ]
