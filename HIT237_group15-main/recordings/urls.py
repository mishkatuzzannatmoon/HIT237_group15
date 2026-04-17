from django.urls import path
from . import views

urlpatterns = [
    path("", views.RecordingListView.as_view(), name="recording_list"),
    path("<int:id>/", views.RecordingDetailView.as_view(), name="recording_detail"),

    path("recordings/", views.RecordingListView.as_view(), name="recording_list_alt"),
    path("recordings/high-confidence/", views.HighConfidenceRecordingListView.as_view(), name="high_confidence_recordings"),
    path("recordings/add/", views.RecordingCreateView.as_view(), name="recording_create"),

    path("species/", views.SpeciesListView.as_view(), name="species_list"),
    path("species/threatened/", views.ThreatenedSpeciesListView.as_view(), name="threatened_species"),
    path("species/add/", views.SpeciesCreateView.as_view(), name="species_create"),
    path("species/<int:pk>/edit/", views.SpeciesUpdateView.as_view(), name="species_update"),
    path("species/<int:pk>/delete/", views.SpeciesDeleteView.as_view(), name="species_delete"),

    path("anomalies/", views.AnomalyListView.as_view(), name="anomaly_list"),
    path("anomalies/flagged/", views.FlaggedAnomalyListView.as_view(), name="flagged_anomalies"),
    path("anomalies/review/", views.NeedsReviewAnomalyListView.as_view(), name="anomalies_needing_review"),
    path("anomalies/add/", views.AnomalyCreateView.as_view(), name="anomaly_create"),
    path("anomalies/<int:pk>/edit/", views.AnomalyUpdateView.as_view(), name="anomaly_update"),
    path("anomalies/<int:pk>/delete/", views.AnomalyDeleteView.as_view(), name="anomaly_delete"),

    path("locations/add/", views.LocationCreateView.as_view(), name="location_create"),
    path("recordings/<int:pk>/delete/", views.RecordingDeleteView.as_view(), name="recording_delete"),
]