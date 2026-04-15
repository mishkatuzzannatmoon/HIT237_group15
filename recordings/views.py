from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Species, Location, Recording, Anomaly
from django.urls import reverse_lazy


recordings_data = [
    {
        "id": 1,
        "species": "Northern Quoll",
        "date": "2026-04-02",
        "location": "Darwin",
        "confidence_score": 92
    },
    {
        "id": 2,
        "species": "Black-footed Tree-rat",
        "date": "2026-04-01",
        "location": "Kakadu",
        "confidence_score": 87
    },
    {
        "id": 3,
        "species": "Gouldian Finch",
        "date": "2026-03-30",
        "location": "Arnhem Land",
        "confidence_score": 95
    }
]


class RecordingListView(View):
    def get(self, request):
        return render(request, "recordings/recording_list.html", {
            "recordings": recordings_data
        })


class RecordingDetailView(View):
    def get(self, request, id):
        selected_recording = None

        for recording in recordings_data:
            if recording["id"] == id:
                selected_recording = recording
                break

        return render(request, "recordings/recording_detail.html", {
            "recording": selected_recording
        })


class UploadRecordingView(View):
    def get(self, request):
        return render(request, "recordings/upload_recording.html")

    def post(self, request):
        species = request.POST.get("species")
        message = f"{species} uploaded successfully!"

        return render(request, "recordings/upload_recording.html", {
            "message": message
        })


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
    success_url = reverse_lazy('species_list')

class SpeciesUpdateView(UpdateView):
    model = Species
    fields = '__all__'
    success_url = reverse_lazy('species_list')

class SpeciesDeleteView(DeleteView):
    model = Species
    success_url = reverse_lazy('species_list')



class RecordingListView(ListView):
    model = Recording
    template_name = 'recordings/recording_list.html'
    context_object_name = 'recordings'
    queryset = Recording.objects.select_related('species', 'location', 'user')

class HighConfidenceRecordingListView(RecordingListView):

    template_name = 'recordings/high_confidence.html'
    def get_queryset(self):
        return Recording.objects.high_confidence().select_related('species', 'location', 'user')

class RecordingCreateView(CreateView):
    model = Recording
    fields = ['species', 'location', 'record_type', 'date_recorded', 'confidence_score']
    success_url = reverse_lazy('recording_list')



class AnomalyListView(ListView):
    model = Anomaly
    template_name = 'anomalies/anomaly_list.html'
    context_object_name = 'anomalies'
    queryset = Anomaly.objects.select_related('recording', 'recording__species')

class FlaggedAnomalyListView(AnomalyListView):
    template_name = 'anomalies/flagged.html'
    def get_queryset(self):
        return Anomaly.objects.flagged()

class NeedsReviewAnomalyListView(AnomalyListView):
    template_name = 'anomalies/review.html'
    def get_queryset(self):
        return Anomaly.objects.needs_review()

class AnomalyCreateView(CreateView):
    model = Anomaly
    fields = ['recording', 'reason']
    success_url = reverse_lazy('anomaly_list')

class AnomalyUpdateView(UpdateView):
    model = Anomaly
    fields = ['reason', 'status']
    success_url = reverse_lazy('anomaly_list')

class AnomalyDeleteView(DeleteView):
    model = Anomaly
    success_url = reverse_lazy('anomaly_list')