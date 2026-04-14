from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
 

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
        max_length=2,
        choices=CONSERVATION_CHOICES,
        default='LC',
    )
 
    class Meta:
        ordering = ['common_name']
        verbose_name_plural = 'Species'
 
    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"
 
    def is_threatened(self):
        return self.conservation_status in ('VU', 'EN', 'CR')

 
class Location(models.Model):
 
    location_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
    )
 
    class Meta:
        ordering = ['location_name']
 
    def __str__(self):
        return self.location_name

    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None
    
 
class Recording(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recordings',
        null=True,
        blank=True,
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,      
        related_name='recordings',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,     
        null=True,
        blank=True,
        related_name='recordings',
    )
 
    audio_file = models.FileField(upload_to='recordings/%Y/%m/', null=True, blank=True)  
    recorded_at = models.DateTimeField()
    uploaded_at = models.DateTimeField(default=timezone.now)
 
   
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Confidence that the species was correctly identified (0.0–1.0)',
    )
 
    notes = models.TextField(blank=True)
 
    class Meta:
        ordering = ['-recorded_at']     
 
    def __str__(self):
        return f"{self.species.common_name} at {self.location} ({self.recorded_at.date()})"
 
    def confidence_percentage(self):
        return f"{self.confidence_score * 100:.1f}%"
 
    def is_high_confidence(self):
        return self.confidence_score >= 0.8
 
    def has_anomalies(self):
        return self.anomalies.exclude(status='resolved').exists()
 
    @classmethod
    def recent(cls, days=30):
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(recorded_at__gte=cutoff)
 
    @classmethod
    def by_threatened_species(cls):
        
        threatened_statuses = ('VU', 'EN', 'CR')
        return cls.objects.filter(
            species__conservation_status__in=threatened_statuses
        ).select_related('species', 'location', 'user')
 

class Anomaly(models.Model):
 
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
 
    recording = models.ForeignKey(
        Recording,
        on_delete=models.CASCADE,      
        related_name='anomalies',
    )
    flagged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,       
        related_name='flagged_anomalies',
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,      
        null=True,
        blank=True,
        related_name='reviewed_anomalies',
    )
 
    reason = models.CharField(max_length=200)
    flagged_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',                
    )
 
    class Meta:
        ordering = ['-flagged_at']    
        verbose_name_plural = 'Anomalies'
 
    def __str__(self):
        return f"Anomaly [{self.get_status_display()}] on {self.recording}"
 
    def is_open(self):
        return self.status == 'open'
 
    def resolve(self, reviewer):
        self.status = 'resolved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
 
    def dismiss(self, reviewer):
        self.status = 'dismissed'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
