
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from .models import AudioRecording, AnomalyFlag, Species
from decimal import Decimal, ROUND_DOWN

# Recording services

def create_recording(user, form_data: dict) -> AudioRecording:

    confidence = form_data.get('confidence_score')
    if confidence is not None and (float(confidence) < 0 or float(confidence) > 1):
        raise ValidationError('Confidence score must be between 0.00 and 1.00.')
    # Normalize numeric values to avoid floating point precision issues
    lat = form_data.get('latitude')
    lon = form_data.get('longitude')
    conf = form_data.get('confidence_score')

    if lat is not None:
        lat = Decimal(str(lat)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
    if lon is not None:
        lon = Decimal(str(lon)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
    if conf is not None:
        conf = Decimal(str(conf)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    recording = AudioRecording(
        recorded_by=user,
        species=form_data['species'],
        recorded_at=form_data['recorded_at'],
        latitude=lat,
        longitude=lon,
        location_name=form_data.get('location_name', ''),
        audio_file=form_data.get('audio_file'),
        confidence_score=conf,
        notes=form_data.get('notes', ''),
    )
    recording.full_clean()
    recording.save()
    return recording


def update_recording(user, recording: AudioRecording, form_data: dict) -> AudioRecording:

    if recording.recorded_by != user:
        raise PermissionDenied('You do not have permission to edit this recording.')

    # Normalize numeric inputs when updating
    for field, value in form_data.items():
        if field in ('latitude', 'longitude') and value is not None:
            value = Decimal(str(value)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
        if field == 'confidence_score' and value is not None:
            value = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        setattr(recording, field, value)

    # Ensure existing numeric fields are quantized to the model precision
    if getattr(recording, 'latitude', None) is not None:
        recording.latitude = Decimal(str(recording.latitude)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
    if getattr(recording, 'longitude', None) is not None:
        recording.longitude = Decimal(str(recording.longitude)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
    if getattr(recording, 'confidence_score', None) is not None:
        recording.confidence_score = Decimal(str(recording.confidence_score)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    recording.full_clean()
    recording.save()
    return recording


def delete_recording(user, recording: AudioRecording) -> None:

    if recording.recorded_by != user:
        raise PermissionDenied('You do not have permission to delete this recording.')
    recording.delete()


def get_recording_or_404(pk: int) -> AudioRecording:

    return get_object_or_404(
        AudioRecording.objects.select_related('species', 'recorded_by')
        .prefetch_related('flags'),
        pk=pk,
    )

# Anomaly services

def flag_recording(user, recording: AudioRecording, reason: str) -> AnomalyFlag:

    if not reason or not reason.strip():
        raise ValidationError('A reason must be provided when flagging a recording.')

    if recording.flags.filter(resolved=True).exists():
        raise PermissionDenied('This recording has already been resolved and cannot be re-flagged.')

    return recording.flag_as_anomaly(reason=reason, flagged_by=user)


def resolve_flag(user, flag: AnomalyFlag) -> AnomalyFlag:

    if flag.resolved:
        raise ValidationError('This flag has already been resolved.')

    flag.resolved = True
    flag.save()
    flag.recording.resolve_flags()
    return flag


def dismiss_flag(user, flag: AnomalyFlag) -> AnomalyFlag:
 
    if flag.resolved:
        raise ValidationError('This flag has already been resolved.')

    flag.resolved = True
    flag.save()
    return flag

# Species services

def create_species(form_data: dict) -> Species:
 
    if Species.objects.filter(scientific_name=form_data['scientific_name']).exists():
        raise ValidationError(
            f"A species with scientific name '{form_data['scientific_name']}' already exists."
        )

    species = Species(**form_data)
    species.full_clean()
    species.save()
    return species
