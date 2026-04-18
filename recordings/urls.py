from django.urls import path
from . import views

urlpatterns = [
    # Species
    path('species/', views.SpeciesListView.as_view(), name='species_list'),
    path('species/add/', views.SpeciesCreateView.as_view(), name='species_create'),
    path('species/<int:pk>/', views.SpeciesDetailView.as_view(), name='species_detail'),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name='species_update'),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name='species_delete'),

    # Recordings
    path('', views.RecordingListView.as_view(), name='recording_list'),
    path('recordings/add/', views.RecordingCreateView.as_view(), name='recording_create'),
    path('recordings/<int:pk>/', views.RecordingDetailView.as_view(), name='recording_detail'),
    path('recordings/<int:pk>/edit/', views.RecordingUpdateView.as_view(), name='recording_update'),
    path('recordings/<int:pk>/delete/', views.RecordingDeleteView.as_view(), name='recording_delete'),

    # Anomalies
    path('anomalies/', views.AnomalyListView.as_view(), name='anomaly_list'),
    path('anomalies/add/<int:recording_pk>/', views.AnomalyCreateView.as_view(), name='anomaly_create'),
    path('anomalies/<int:pk>/edit/', views.AnomalyUpdateView.as_view(), name='anomaly_update'),
    path('anomalies/<int:pk>/delete/', views.AnomalyDeleteView.as_view(), name='anomaly_delete'),
]