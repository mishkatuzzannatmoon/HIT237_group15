from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Species(models.Model):
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)  
    description = models.CharField(max_length=500)
    
    def __str__(self):
        return self.common_name
    
class Location(models.Model):
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.location_name   
    
class Recording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    audio_recording = models.FileField(upload_to='recordings/')
    recorded_at = models.DateTimeField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    confidenceScore = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.species.common_name} recorded by {self.user.username} at {self.location.location_name}"
    
class Anomaly(models.Model):
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE)
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE)

    reason = models.CharField(max_length=200)
    flagged_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Anomaly flagged for {self.recording} by {self.flagged_by.username}"

