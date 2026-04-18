from django.contrib import admin
from .models import Species, AudioRecording, AnomalyFlag


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display  = ['common_name', 'scientific_name', 'conservation_status', 'is_native', 'not_native']
    list_filter   = ['conservation_status', 'is_native', 'not_native']
    search_fields = ['common_name', 'scientific_name']
    ordering      = ['scientific_name']


class AnomalyFlagInline(admin.TabularInline):
    model  = AnomalyFlag
    extra  = 0
    fields = ['reason', 'resolved', 'flagged_by']
    readonly_fields = ['flagged_by']


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display  = ['species', 'location_name', 'recorded_at', 'confidence_score', 'is_anomaly']
    list_filter   = ['is_anomaly', 'species__conservation_status']
    search_fields = ['species__common_name', 'location_name']
    ordering      = ['-recorded_at']
    inlines       = [AnomalyFlagInline]


@admin.register(AnomalyFlag)
class AnomalyFlagAdmin(admin.ModelAdmin):
    list_display  = ['recording', 'flagged_by', 'resolved']
    list_filter   = ['resolved']
    search_fields = ['recording__species__common_name', 'reason']