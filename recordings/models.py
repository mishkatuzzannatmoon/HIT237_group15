from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
 
from .managers import RecordingManager
 
class ConservationStatus(models.TextChoices):
   
    LEAST_CONCERN         = 'LC', 'Least Concern'
    NEAR_THREATENED       = 'NT', 'Near Threatened'
    VULNERABLE            = 'VU', 'Vulnerable'
    ENDANGERED            = 'EN', 'Endangered'
    CRITICALLY_ENDANGERED = 'CR', 'Critically Endangered'
    DATA_DEFICIENT        = 'DD', 'Data Deficient'
    NOT_EVALUATED         = 'NE', 'Not Evaluated'
 
 
class Species(models.Model):

    common_name         = models.CharField(max_length=200)
    scientific_name     = models.CharField(max_length=200, unique=True)
    conservation_status = models.CharField(
        max_length=2,
        choices=ConservationStatus.choices,
        default=ConservationStatus.NOT_EVALUATED,
    )
    is_native  = models.BooleanField(default=False)
    not_native   = models.BooleanField(default=False)
    description = models.TextField(blank=True)
 
    class Meta:
        verbose_name_plural = 'species'
        ordering = ['scientific_name']
 
    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"
 
    def get_absolute_url(self):
        return reverse('recordings:species-detail', kwargs={'pk': self.pk})
 
    @property
    def conversation_status(self):
        """Convenience property used in templates and admin."""
        return self.conservation_status in (
            ConservationStatus.VULNERABLE,
            ConservationStatus.ENDANGERED,
            ConservationStatus.CRITICALLY_ENDANGERED,
            ConservationStatus.DATA_DEFICIENT,
            ConservationStatus.NOT_EVALUATED,
            ConservationStatus.NEAR_THREATENED,
            ConservationStatus.LEAST_CONCERN,
        )
 
class RecordType(models.TextChoices):
        
        HUMAN_OBSERVATION    = 'HO', 'Human Observation'
        MACHINE_OBSERVATION  = 'MO', 'Machine Observation'
        PRESERVED_SPECIMEN   = 'PS', 'Preserved Specimen'
        MATERIAL_SAMPLE      = 'MS', 'Material Sample'
        OTHER                = 'OTHER', 'Other'

 
class AudioRecording(models.Model):
 
    """
    An audio observation logged by a researcher or citizen scientist.
 
    Relationships:
      species      — PROTECT: cannot delete a Species that has recordings
      recorded_by  — SET_NULL: recordings survive if a user is deleted
    """
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,     
        related_name='recordings',
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recordings',
    )
    recorded_at   = models.DateTimeField()
    latitude      = models.DecimalField(max_digits=9, decimal_places=6)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=200, blank=True)
    record_type   = models.CharField(max_length=20, choices=RecordType.choices, default=RecordType.HUMAN_OBSERVATION)
 
    audio_file = models.FileField(
        upload_to='recordings/%Y/%m/',
        blank=True,
        null=True,
    )
 
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="0.00 = no confidence, 1.00 = certain",
    )
    notes      = models.TextField(blank=True)
    is_anomaly = models.BooleanField(default=False, db_index=True)
 
    #Custom manager - managers.py
    objects = RecordingManager()
 
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['species', '-recorded_at']),
        ]
 
    def __str__(self):
        return (
            f"{self.species.common_name} at "
            f"{self.location_name or 'unknown location'} "
            f"on {self.recorded_at.strftime('%Y-%m-%d')}"
        )
 
    def get_absolute_url(self):
        return reverse('recordings:detail', kwargs={'pk': self.pk})
 
    def flag_as_anomaly(self, reason: str, flagged_by) -> 'AnomalyFlag':
    
        self.is_anomaly = True
        self.save(update_fields=['is_anomaly'])
        return AnomalyFlag.objects.create(
            recording=self,
            reason=reason,
            flagged_by=flagged_by,
        )
 
    def resolve_flags(self):
        """Mark all open flags on this recording as resolved."""
        self.flags.filter(resolved=False).update(resolved=True)
        self.is_anomaly = False
        self.save(update_fields=['is_anomaly'])

    @property
    def has_been_flagged(self):
        return self.flags.exists()
 
 
class AnomalyFlag(models.Model):
    """
    An audit record created when a user flags a recording as anomalous.
    One recording can accumulate multiple flags from different users.
    """
    recording = models.ForeignKey(
        AudioRecording,
        on_delete=models.CASCADE,
        related_name='flags',
    )
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='raised_flags',
    )
    reason   = models.TextField()
    resolved = models.BooleanField(default=False)
 
    class Meta:
        ordering = ['-id']
 
    def __str__(self):
        return f"Flag #{self.pk} on recording #{self.recording_id}"