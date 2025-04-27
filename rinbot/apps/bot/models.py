from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField


class Admins(models.Model):
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
    
    def __str__(self):
        return f"{self.user_name} in {self.guild_name}"


class AutoRole(models.Model):
    active = models.BooleanField(default=True)
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100)
    role_id = models.BigIntegerField()
    role_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('guild_id', 'role_id')
        verbose_name = "Auto Role"
        verbose_name_plural = "Auto Roles"

    def __str__(self):
        return f"{self.role_name} in {self.guild_name}"


class Birthdays(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=100)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=100)
    user_locale = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('date', 'user_id')
        verbose_name = "Birthday"
        verbose_name_plural = "Birthdays"

    def __str__(self):
        return f"{self.name} on {self.date}"


class Blacklist(models.Model):
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('guild_id', 'user_id')

    def __str__(self):
        return f"{self.user_name or self.user_id} in {self.guild_name or self.guild_id}"


class FavouriteTracks(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    duration = models.CharField(max_length=50, null=True, blank=True)
    uploader = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Favourite Track"
        verbose_name_plural = "Favourite Tracks"

    def __str__(self):
        return self.title or self.url


class FavouritePlaylists(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    count = models.IntegerField()
    uploader = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Favourite Playlist"
        verbose_name_plural = "Favourite Playlists"

    def __str__(self):
        return self.title or self.url


class Guilds(models.Model):
    guild_id = models.BigIntegerField(primary_key=True)
    guild_name = models.CharField(max_length=100)
    user_count = models.IntegerField()

    class Meta:
        verbose_name = "Guild"
        verbose_name_plural = "Guilds"

    def __str__(self):
        return self.guild_name


class GuildConfig(models.Model):
    SPAM_FILTER_CHOICES = [
        (0, "Disabled"),
        (1, "Delete"),
        (2, "Kick")
    ]
    
    guild = models.OneToOneField(Guilds, on_delete=models.CASCADE, related_name='config')
    spam_filter_action = models.IntegerField(
        choices=SPAM_FILTER_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
    spam_filter_message = models.TextField(null=True, blank=True)
    spam_filter_original_state = models.IntegerField(
        default=0,
        choices=SPAM_FILTER_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
    
    class Meta:
        verbose_name = "Guild Configuration"
        verbose_name_plural = "Guild Configurations"

    def __str__(self):
        return f"Config for {self.guild.guild_name}"


class Owners(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Owner"
        verbose_name_plural = "Owners"

    def __str__(self):
        return self.user_name


class Users(models.Model):
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=100)
    global_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    roles = ArrayField(models.CharField(max_length=100))

    class Meta:
        unique_together = ('guild_id', 'user_id')
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.display_name} in {self.guild_name}"


class UserConfig(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='config')
    translate_private = models.BooleanField(default=False)
    fact_check_private = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Configuration"
        verbose_name_plural = "User Configurations"

    def __str__(self):
        return f"Config for {self.user.display_name}"


class Warns(models.Model):
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=100)
    moderator_id = models.BigIntegerField()
    moderator_name = models.CharField(max_length=100)
    warn = models.TextField()
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = "Warning"
        verbose_name_plural = "Warnings"

    def __str__(self):
        return f"Warning for {self.user_name} in {self.guild_name}"


class WelcomeChannels(models.Model):
    SHOW_PFP_CHOICES = [
        (0, "Don't Show"),
        (1, "Show Small"),
        (2, "Show Large")
    ]
    
    guild_id = models.BigIntegerField()
    guild_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    channel_id = models.BigIntegerField()
    channel_name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    colour = models.CharField(max_length=7)  # Hex colour code
    show_pfp = models.IntegerField(
        choices=SHOW_PFP_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )

    class Meta:
        unique_together = ('guild_id', 'channel_id')
        verbose_name = "Welcome Channel"
        verbose_name_plural = "Welcome Channels"

    def __str__(self):
        return f"{self.channel_name} in {self.guild_name}"
