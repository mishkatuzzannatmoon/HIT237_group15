from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Species, AudioRecording, AnomalyFlag


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

 
class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = ['common_name', 'scientific_name', 'conservation_status',
                  'is_native', 'not_native', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
 
 
class AudioRecordingForm(forms.ModelForm):
    class Meta:
        model = AudioRecording
        fields = ['species', 'recorded_at', 'latitude', 'longitude',
                  'location_name', 'record_type', 'audio_file', 'confidence_score', 'notes']
        widgets = {
            'recorded_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
 
 
class AnomalyFlagForm(forms.ModelForm):
    class Meta:
        model = AnomalyFlag
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
 
