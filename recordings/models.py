from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import QuerySet
 
class SpeciesQuerySet(QuerySet):
    def threatened(self):
        return self.filter(conservation_status__in=['VU', 'EN', 'CR'])

class Species(models.Model):
 
    CONSERVATION_CHOICES = [       
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EX', 'Extinct'),
    ]
 
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(blank=True)
    conservation_status = models.CharField(max_length=2, choices=CONSERVATION_CHOICES, default='VU') 
 
    class Meta:
        ordering = ['common_name']  
 
    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"
 
    def threatened(self):
        return self.conservation_status in ('VU', 'EN', 'CR')
        
objects = SpeciesQuerySet.as_manager()
 

class Location(models.Model):

    location_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0) 
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
 
    def __str__(self):
        return self.location_name
 
class RecordingQuerySet(QuerySet):
    def high_confidence(self):
        return self.filter(confidence_score__gte=80)

    def medium_confidence(self):
        return self.filter(confidence_score__gte=50, confidence_score__lt=80)

    def low_confidence(self):
        return self.filter(confidence_score__lt=50)
 
class Recording(models.Model):

    RECORD_CHOICES = [              
        ('human_observation', 'Human Observation'),
        ('machine_observation', 'Machine Observation'),
        ('preserved_specimen', 'Preserved Specimen'),
        ('material_sample', 'Material Sample'),
    ]
 
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='recordings', null=True, blank=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='recordings', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='recordings', null=True, blank=True)
    record_type = models.CharField(max_length=20, choices=RECORD_CHOICES, default='human_observation')
    date_recorded = models.DateField(default=timezone.now)
    confidence_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default = 0, help_text='Confidence score from 0 to 100')
 
    class Meta:
        ordering = ['-date_recorded']  
 
    def __str__(self):
        return f"{self.species.common_name} — {self.date_recorded}"
 
    def high_confidence(self):
        return self.confidence_score >= 80
 
    def confidence_label(self):
        if self.confidence_score >= 80:
            return 'High'
        elif self.confidence_score >= 50:
            return 'Medium'
        else:
            return 'Low'
 
objects = RecordingQuerySet.as_manager()

class AnomalyQuerySet(QuerySet):
    def flagged(self):
        return self.filter(status='open')

    def needs_review(self):
        return self.filter(status__in=['open', 'under_review'])

    def resolved(self):
        return self.filter(status='resolved')

 
class Anomaly(models.Model):

    STATUS_CHOICES = [        
        ('resolved', 'Resolved'),
        ('under_review', 'Under Review'),
        ('open', 'Open'),
    ]

    ANOMALY_REASONS = [
        ('misidentification', 'Misidentification'),
        ('data_error', 'Data Error'),
        ('unusual_location', 'Unusual Location'),
        ('other', 'Other'),
    ]

    recording = models.ForeignKey(Recording, on_delete=models.CASCADE,related_name='anomalies')
    reason = models.CharField(max_length=20, choices=ANOMALY_REASONS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    class Meta:
        ordering = ['-id']         
 
    def __str__(self):
        return f"Anomaly [{self.get_status_display()}] on {self.recording}"
 
    def is_flagged(self):
        return self.status == 'open'
 
    def needs_review(self):
        return self.status in ('under_review', 'open')
 
    def save(self, *args, **kwargs):
        score = self.recording.confidence_score  
        if score < 50:
            self.status = 'open'
        elif score < 80:
            self.status = 'under_review'
        else:
            self.status = 'resolved'
        super().save(*args, **kwargs)

objects = AnomalyQuerySet.as_manager()
