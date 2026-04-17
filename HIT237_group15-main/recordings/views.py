from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Species, Location, Recording, Anomaly


class SpeciesListView(ListView):
    model = Species
    template_name = 'species/species_list.html'
    context_object_name = 'species'


class ThreatenedSpeciesListView(SpeciesListView):
    template_name = 'species/threatened_species.html'

    def get_queryset(self):
        return Species.objects.threatened()


class SpeciesCreateView(CreateView):
    model = Species
    fields = '__all__'
    template_name = 'species/species_form.html'
    success_url = reverse_lazy('species_list')


class SpeciesUpdateView(UpdateView):
    model = Species
    fields = '__all__'
    template_name = 'species/species_form.html'
    success_url = reverse_lazy('species_list')


class SpeciesDeleteView(DeleteView):
    model = Species
    template_name = 'species/species_confirm_delete.html'
    success_url = reverse_lazy('species_list')


class RecordingListView(ListView):
    model = Recording
    template_name = 'recordings/recording_list.html'
    context_object_name = 'recordings'
    queryset = Recording.objects.select_related('species', 'location', 'user')


class RecordingDetailView(DetailView):
    model = Recording
    template_name = 'recordings/recording_detail.html'
    context_object_name = 'recording'
    pk_url_kwarg = 'id'


class HighConfidenceRecordingListView(RecordingListView):
    template_name = 'recordings/high_confidence.html'

    def get_queryset(self):
        return Recording.objects.high_confidence().select_related('species', 'location', 'user')


class RecordingCreateView(CreateView):
    model = Recording
    fields = ['species', 'location', 'record_type', 'date_recorded', 'confidence_score']
    template_name = 'recordings/recording_form.html'
    success_url = reverse_lazy('recording_list')


class AnomalyListView(ListView):
    model = Anomaly
    template_name = 'anomalies/anomaly_list.html'
    context_object_name = 'anomalies'
    queryset = Anomaly.objects.select_related('recording', 'recording__species')


class FlaggedAnomalyListView(AnomalyListView):
    template_name = 'anomalies/flagged.html'

    def get_queryset(self):
        return Anomaly.objects.flagged().select_related('recording', 'recording__species')


class NeedsReviewAnomalyListView(AnomalyListView):
    template_name = 'anomalies/review.html'

    def get_queryset(self):
        return Anomaly.objects.needs_review().select_related('recording', 'recording__species')


class AnomalyCreateView(CreateView):
    model = Anomaly
    fields = ['recording', 'reason']
    template_name = 'anomalies/anomaly_form.html'
    success_url = reverse_lazy('anomaly_list')


class AnomalyUpdateView(UpdateView):
    model = Anomaly
    fields = ['reason', 'status']
    template_name = 'anomalies/anomaly_form.html'
    success_url = reverse_lazy('anomaly_list')


class AnomalyDeleteView(DeleteView):
    model = Anomaly
    template_name = 'anomalies/anomaly_confirm_delete.html'
    success_url = reverse_lazy('anomaly_list')


class LocationCreateView(CreateView):
    model = Location
    fields = '__all__'
    template_name = 'locations/location_form.html'
    success_url = reverse_lazy('recording_create')


class RecordingDeleteView(DeleteView):
    model = Recording
    template_name = 'recordings/recording_confirm_delete.html'
    success_url = reverse_lazy('recording_list')