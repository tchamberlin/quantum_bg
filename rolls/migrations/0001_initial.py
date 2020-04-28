# Generated by Django 3.0.3 on 2020-04-28 01:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Hand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cards', models.ManyToManyField(to='rolls.Card')),
            ],
        ),
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attacker_advantage', models.IntegerField(help_text='The difference in ship die value between the attacker and defender (i.e. attacker - defender)')),
                ('attacker_win_ratio', models.FloatField()),
                ('num_trials', models.IntegerField(help_text='Number of trials over which attacker_win_ratio was calculated')),
                ('attacker_hand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encounters_as_attacker', to='rolls.Hand')),
                ('defender_hand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encounters_as_defender', to='rolls.Hand')),
            ],
        ),
    ]
