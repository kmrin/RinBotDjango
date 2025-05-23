# Generated by Django 5.2 on 2025-04-28 13:47

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(max_length=100)),
                ('user_id', models.BigIntegerField()),
                ('user_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Admin',
                'verbose_name_plural': 'Admins',
            },
        ),
        migrations.CreateModel(
            name='FavouritePlaylists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField()),
                ('count', models.IntegerField()),
                ('uploader', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Favourite Playlist',
                'verbose_name_plural': 'Favourite Playlists',
            },
        ),
        migrations.CreateModel(
            name='FavouriteTracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField()),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
                ('uploader', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Favourite Track',
                'verbose_name_plural': 'Favourite Tracks',
            },
        ),
        migrations.CreateModel(
            name='Guilds',
            fields=[
                ('guild_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('guild_name', models.CharField(max_length=100)),
                ('user_count', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Guild',
                'verbose_name_plural': 'Guilds',
            },
        ),
        migrations.CreateModel(
            name='Owners',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Owner',
                'verbose_name_plural': 'Owners',
            },
        ),
        migrations.CreateModel(
            name='Warns',
            fields=[
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(max_length=100)),
                ('user_id', models.BigIntegerField()),
                ('user_name', models.CharField(max_length=100)),
                ('moderator_id', models.BigIntegerField()),
                ('moderator_name', models.CharField(max_length=100)),
                ('warn', models.TextField()),
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Warning',
                'verbose_name_plural': 'Warnings',
            },
        ),
        migrations.CreateModel(
            name='AutoRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(max_length=100)),
                ('role_id', models.BigIntegerField()),
                ('role_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Auto Role',
                'verbose_name_plural': 'Auto Roles',
                'unique_together': {('guild_id', 'role_id')},
            },
        ),
        migrations.CreateModel(
            name='Birthdays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('user_id', models.BigIntegerField()),
                ('user_name', models.CharField(max_length=100)),
                ('user_locale', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Birthday',
                'verbose_name_plural': 'Birthdays',
                'unique_together': {('day', 'month', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='Blacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(blank=True, max_length=100, null=True)),
                ('user_id', models.BigIntegerField()),
                ('user_name', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'unique_together': {('guild_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='GuildConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spam_filter_action', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Delete'), (2, 'Kick')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)])),
                ('spam_filter_message', models.TextField(blank=True, null=True)),
                ('spam_filter_original_state', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Delete'), (2, 'Kick')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)])),
                ('guild', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to='bot.guilds')),
            ],
            options={
                'verbose_name': 'Guild Configuration',
                'verbose_name_plural': 'Guild Configurations',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(max_length=100)),
                ('user_id', models.BigIntegerField()),
                ('user_name', models.CharField(max_length=100)),
                ('global_name', models.CharField(max_length=100)),
                ('display_name', models.CharField(max_length=100)),
                ('roles', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'unique_together': {('guild_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translate_private', models.BooleanField(default=False)),
                ('fact_check_private', models.BooleanField(default=False)),
                ('birthday_notifications', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to='bot.users')),
            ],
            options={
                'verbose_name': 'User Configuration',
                'verbose_name_plural': 'User Configurations',
            },
        ),
        migrations.CreateModel(
            name='WelcomeChannels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guild_id', models.BigIntegerField()),
                ('guild_name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('channel_id', models.BigIntegerField()),
                ('channel_name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('colour', models.CharField(max_length=7)),
                ('show_pfp', models.IntegerField(choices=[(0, "Don't Show"), (1, 'Show Small'), (2, 'Show Large')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)])),
            ],
            options={
                'verbose_name': 'Welcome Channel',
                'verbose_name_plural': 'Welcome Channels',
                'unique_together': {('guild_id', 'channel_id')},
            },
        ),
    ]
