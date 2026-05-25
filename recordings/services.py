
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from .models import AudioRecording, AnomalyFlag, Species

# Recording services

def create_recording(user, form_data: dict) -> AudioRecording:

    confidence = form_data.get('confidence_score')
    if confidence is not None and (float(confidence) < 0 or float(confidence) > 1):
        raise ValidationError('Confidence score must be between 0.00 and 1.00.')

    recording = AudioRecording(
        recorded_by=user,
        species=form_data['species'],
        recorded_at=form_data['recorded_at'],
        latitude=form_data['latitude'],
        longitude=form_data['longitude'],
        location_name=form_data.get('location_name', ''),
        audio_file=form_data.get('audio_file'),
        confidence_score=form_data['confidence_score'],
        notes=form_data.get('notes', ''),
    )
    recording.full_clean()
    recording.save()
    return recording


def update_recording(user, recording: AudioRecording, form_data: dict) -> AudioRecording:

    if recording.recorded_by != user:
        raise PermissionDenied('You do not have permission to edit this recording.')

    for field, value in form_data.items():
        setattr(recording, field, value)

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
