# Generated by Django 4.2 on 2024-07-05 04:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='round',
            options={'verbose_name': 'тур', 'verbose_name_plural': 'туры'},
        ),
        migrations.RemoveField(
            model_name='round',
            name='order',
        ),
    ]
