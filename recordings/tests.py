from django.test import TestCase

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
 
from .models import Species, AudioRecording, AnomalyFlag, ConservationStatus, RecordType
from . import services
 
def make_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username=username, password=password)
 
 
def make_species(common_name='Test Bird', scientific_name='Testus birdus',
                 conservation_status=ConservationStatus.VULNERABLE):
    return Species.objects.create(
        common_name=common_name,
        scientific_name=scientific_name,
        conservation_status=conservation_status,
        is_native=True,
        not_native=False,
    )
 
 
def make_recording(user, species, confidence=0.85, location='Test Location'):
    from django.utils import timezone
    return AudioRecording.objects.create(
        recorded_by=user,
        species=species,
        recorded_at=timezone.now(),
        latitude=-12.461,
        longitude=130.841,
        location_name=location,
        confidence_score=confidence,
        record_type=RecordType.HUMAN_OBSERVATION,
    )
 
 
# Model tests

 
class SpeciesModelTest(TestCase):
 
    def test_str_returns_common_and_scientific_name(self):
        species = make_species()
        self.assertEqual(str(species), 'Test Bird (Testus birdus)')
 
    def test_scientific_name_is_unique(self):
        make_species()
        with self.assertRaises(Exception):
            make_species() 
 

 
 
class AudioRecordingModelTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.species = make_species()
 
    def test_str_includes_species_and_location(self):
        recording = make_recording(self.user, self.species)
        self.assertIn('Test Bird', str(recording))
        self.assertIn('Test Location', str(recording))
 
    def test_high_confidence_true_at_threshold(self):
        recording = make_recording(self.user, self.species, confidence=0.80)
        self.assertTrue(recording.is_anomaly is False)
 
    def test_has_been_flagged_false_initially(self):
        recording = make_recording(self.user, self.species)
        self.assertFalse(recording.has_been_flagged)
 
    def test_flag_as_anomaly_sets_is_anomaly(self):
        recording = make_recording(self.user, self.species)
        recording.flag_as_anomaly(reason='Test reason', flagged_by=self.user)
        recording.refresh_from_db()
        self.assertTrue(recording.is_anomaly)
 
    def test_resolve_flags_clears_is_anomaly(self):
        recording = make_recording(self.user, self.species)
        recording.flag_as_anomaly(reason='Test', flagged_by=self.user)
        recording.resolve_flags()
        recording.refresh_from_db()
        self.assertFalse(recording.is_anomaly)
 
    def test_meta_ordering_newest_first(self):
        from django.utils import timezone
        from datetime import timedelta
        r1 = make_recording(self.user, self.species)
        r2 = AudioRecording.objects.create(
            recorded_by=self.user,
            species=self.species,
            recorded_at=timezone.now() - timedelta(days=1),
            latitude=-12.0,
            longitude=130.0,
            confidence_score=0.5,
            record_type=RecordType.HUMAN_OBSERVATION,
        )
        recordings = list(AudioRecording.objects.all())
        self.assertEqual(recordings[0], r1)  # newest first
 
 
class RecordingQuerySetTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.species = make_species()
 
    def test_high_confidence_filters_correctly(self):
        make_recording(self.user, self.species, confidence=0.90)
        make_recording(self.user, self.species, confidence=0.40)
        qs = AudioRecording.objects.high_confidence()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(float(qs.first().confidence_score), 0.90)
 
    def test_low_confidence_filters_correctly(self):
        make_recording(self.user, self.species, confidence=0.90)
        make_recording(self.user, self.species, confidence=0.30)
        qs = AudioRecording.objects.low_confidence()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(float(qs.first().confidence_score), 0.30)
 
    def test_anomalies_filters_flagged_recordings(self):
        r1 = make_recording(self.user, self.species)
        r2 = make_recording(self.user, self.species)
        r1.flag_as_anomaly(reason='Test', flagged_by=self.user)
        self.assertEqual(AudioRecording.objects.anomalies().count(), 1)
 
    def test_by_species_filters_correctly(self):
        other_species = make_species(
            common_name='Other', scientific_name='Other species'
        )
        make_recording(self.user, self.species)
        make_recording(self.user, other_species)
        qs = AudioRecording.objects.by_species(self.species.pk)
        self.assertEqual(qs.count(), 1)
 
 
# Service tests
 
class CreateRecordingServiceTest(TestCase):
 
    def setUp(self):
        from django.utils import timezone
        self.user = make_user()
        self.species = make_species()
        self.valid_data = {
            'species': self.species,
            'recorded_at': timezone.now(),
            'latitude': -12.461,
            'longitude': 130.841,
            'location_name': 'Darwin',
            'confidence_score': 0.75,
            'record_type': RecordType.HUMAN_OBSERVATION,
            'notes': '',
        }
 
    def test_create_recording_returns_recording(self):
        recording = services.create_recording(self.user, self.valid_data)
        self.assertIsInstance(recording, AudioRecording)
        self.assertEqual(recording.recorded_by, self.user)
 
    def test_create_recording_sets_species(self):
        recording = services.create_recording(self.user, self.valid_data)
        self.assertEqual(recording.species, self.species)
 
    def test_create_recording_raises_on_invalid_confidence(self):
        self.valid_data['confidence_score'] = 1.5
        with self.assertRaises(ValidationError):
            services.create_recording(self.user, self.valid_data)
 
 
class UpdateRecordingServiceTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(username='other')
        self.species = make_species()
        self.recording = make_recording(self.user, self.species)
 
    def test_owner_can_update(self):
        services.update_recording(
            self.user, self.recording, {'location_name': 'Updated'}
        )
        self.recording.refresh_from_db()
        self.assertEqual(self.recording.location_name, 'Updated')
 
    def test_non_owner_cannot_update(self):
        with self.assertRaises(PermissionDenied):
            services.update_recording(
                self.other_user, self.recording, {'location_name': 'Hacked'}
            )
 
 
class DeleteRecordingServiceTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(username='other')
        self.species = make_species()
        self.recording = make_recording(self.user, self.species)
 
    def test_owner_can_delete(self):
        pk = self.recording.pk
        services.delete_recording(self.user, self.recording)
        self.assertFalse(AudioRecording.objects.filter(pk=pk).exists())
 
    def test_non_owner_cannot_delete(self):
        with self.assertRaises(PermissionDenied):
            services.delete_recording(self.other_user, self.recording)
 
 
class FlagRecordingServiceTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.species = make_species()
        self.recording = make_recording(self.user, self.species)
 
    def test_flag_creates_anomaly_flag(self):
        flag = services.flag_recording(self.user, self.recording, 'Suspicious')
        self.assertIsInstance(flag, AnomalyFlag)
 
    def test_flag_sets_is_anomaly_on_recording(self):
        services.flag_recording(self.user, self.recording, 'Suspicious')
        self.recording.refresh_from_db()
        self.assertTrue(self.recording.is_anomaly)
 
    def test_flag_raises_on_empty_reason(self):
        with self.assertRaises(ValidationError):
            services.flag_recording(self.user, self.recording, '')
 
    def test_cannot_reflag_resolved_recording(self):
        flag = services.flag_recording(self.user, self.recording, 'Test')
        services.resolve_flag(self.user, flag)
        with self.assertRaises(PermissionDenied):
            services.flag_recording(self.user, self.recording, 'Again')
 
 
class ResolveFlagServiceTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.species = make_species()
        self.recording = make_recording(self.user, self.species)
        self.flag = services.flag_recording(self.user, self.recording, 'Test')
 
    def test_resolve_sets_resolved_true(self):
        services.resolve_flag(self.user, self.flag)
        self.flag.refresh_from_db()
        self.assertTrue(self.flag.resolved)
 
    def test_resolve_clears_is_anomaly_on_recording(self):
        services.resolve_flag(self.user, self.flag)
        self.recording.refresh_from_db()
        self.assertFalse(self.recording.is_anomaly)
 
    def test_cannot_resolve_already_resolved_flag(self):
        services.resolve_flag(self.user, self.flag)
        with self.assertRaises(ValidationError):
            services.resolve_flag(self.user, self.flag)
 
 
# View / permission tests

class RecordingListViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.species = make_species()
        make_recording(self.user, self.species)
 
    def test_recording_list_accessible_without_login(self):
        response = self.client.get(reverse('recording_list'))
        self.assertEqual(response.status_code, 200)
 
    def test_recording_list_shows_recordings(self):
        response = self.client.get(reverse('recording_list'))
        self.assertContains(response, 'Test Bird')
 
 
class RecordingCreateViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.species = make_species()
 
    def test_create_redirects_to_login_if_not_authenticated(self):
        response = self.client.get(reverse('recording_create'))
        self.assertRedirects(
            response, f"/login/?next={reverse('recording_create')}"
        )
 
    def test_create_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recording_create'))
        self.assertEqual(response.status_code, 200)
 
 
class RecordingUpdateDeletePermissionTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.owner = make_user(username='owner')
        self.other = make_user(username='other')
        self.species = make_species()
        self.recording = make_recording(self.owner, self.species)
 
    def test_non_owner_cannot_access_edit_view(self):
        self.client.login(username='other', password='testpass123')
        response = self.client.get(
            reverse('recording_update', kwargs={'pk': self.recording.pk})
        )
        self.assertEqual(response.status_code, 403)
 
    def test_owner_can_access_edit_view(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(
            reverse('recording_update', kwargs={'pk': self.recording.pk})
        )
        self.assertEqual(response.status_code, 200)
 
    def test_non_owner_cannot_access_delete_view(self):
        self.client.login(username='other', password='testpass123')
        response = self.client.get(
            reverse('recording_delete', kwargs={'pk': self.recording.pk})
        )
        self.assertEqual(response.status_code, 403)
 
 
class AuthViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
 
    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
 
    def test_register_page_accessible(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
 
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('recording_list'))
 
    def test_login_with_valid_credentials(self):
        make_user(username='logintest', password='testpass123')
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
 
    def test_login_with_invalid_credentials_stays_on_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'nobody',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
 
    def test_logout_requires_post(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)

class RegisterForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ['username', 'password1', 'password2']


