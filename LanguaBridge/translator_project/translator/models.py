from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Translation(models.Model):
    user                 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translations', null=True, blank=True)
    source_text          = models.TextField()
    translated_text      = models.TextField()
    source_language      = models.CharField(max_length=20)
    target_language      = models.CharField(max_length=20)
    source_language_name = models.CharField(max_length=100)
    target_language_name = models.CharField(max_length=100)
    character_count      = models.IntegerField(default=0)
    ip_address           = models.GenericIPAddressField(null=True, blank=True)
    created_at           = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source_language_name} → {self.target_language_name}: {self.source_text[:40]}"

    def save(self, *args, **kwargs):
        self.character_count = len(self.source_text)
        super().save(*args, **kwargs)


class FavoriteTranslation(models.Model):
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='favorites')
    label       = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"⭐ {self.translation}"