from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Species(models.Model):
    CONSERVATION_CHOICES = [
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
    ]
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    conservation_status = models.CharField(
        max_length=2, choices=CONSERVATION_CHOICES, default='LC'
    )

class Location(models.Model):
    location_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)

class Recording(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField()
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        ordering = ['-recorded_at']

    def confidence_percentage(self):
        return f"{self.confidence_score * 100:.1f}%"

    def is_high_confidence(self):
        return self.confidence_score >= 0.8

    def has_anomalies(self):
        return self.anomalies.filter(status!='resolved').exists()

    @classmethod
    def recent(cls, days=30):
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(recorded_at__gte=cutoff)

class Anomaly(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE, related_name='anomalies')
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flagged_anomalies')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_anomalies')
    reason = models.CharField(max_length=200)
    flagged_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')