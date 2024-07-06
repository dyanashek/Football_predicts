# Generated by Django 4.2 on 2024-07-05 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_predict_score1_alter_predict_score2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='predict',
            options={'ordering': ('-updated_at',), 'verbose_name': 'матч', 'verbose_name_plural': 'матчи'},
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True, verbose_name='Название рейтинга')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
                ('order', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Порядок')),
                ('rounds', models.ManyToManyField(blank=True, to='core.round', verbose_name='Туры в рейтинге')),
            ],
            options={
                'verbose_name': 'рейтинг',
                'verbose_name_plural': 'рейтинги',
                'ordering': ('order',),
            },
        ),
    ]