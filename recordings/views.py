from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Species, AudioRecording, AnomalyFlag, ConservationStatus, RecordType
from .forms import SpeciesForm, AudioRecordingForm, AnomalyFlagForm
from django.shortcuts import redirect

class SpeciesListView(ListView):
    model               = Species
    template_name       = 'recordings/species_list.html'
    context_object_name = 'species_list'
 
 
class SpeciesDetailView(DetailView):
    model         = Species
    template_name = 'recordings/species_detail.html'
 
 
class SpeciesCreateView(CreateView):
    model         = Species
    form_class    = SpeciesForm
    template_name = 'recordings/species_form.html'
    success_url   = reverse_lazy('species_list')
 
 
class SpeciesUpdateView(UpdateView):
    model         = Species
    form_class    = SpeciesForm
    template_name = 'recordings/species_form.html'
    success_url   = reverse_lazy('species_list')
 
 
class SpeciesDeleteView(DeleteView):
    model         = Species
    template_name = 'recordings/species_confirm_delete.html'
    success_url   = reverse_lazy('species_list')
 
class RecordingListView(ListView):
    model               = AudioRecording
    template_name       = 'recordings/recording_list.html'
    context_object_name = 'recordings'
 
    def get_queryset(self):
        return (
        AudioRecording.objects
        .with_details()
        .filter_by_params(self.request)
    )
 
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['all_species']           = Species.objects.order_by('common_name')
        context['conservation_choices']  = ConservationStatus.choices
        context['record_type_choices']   = RecordType.choices
        return context
 
class RecordingDetailView(DetailView):
    model         = AudioRecording
    template_name = 'recordings/recording_detail.html'
 
    def get_queryset(self):
        return AudioRecording.objects.select_related('species', 'recorded_by').prefetch_related('flags')
 
 
class RecordingCreateView(CreateView):
    model         = AudioRecording
    form_class    = AudioRecordingForm
    template_name = 'recordings/recording_form.html'
    success_url   = reverse_lazy('recording_list')
 
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.recorded_by = self.request.user
        return super().form_valid(form)
 
 
class RecordingUpdateView(UpdateView):
    model         = AudioRecording
    form_class    = AudioRecordingForm
    template_name = 'recordings/recording_form.html'
    success_url   = reverse_lazy('recording_list')
 
 
class RecordingDeleteView(DeleteView):
    model         = AudioRecording
    template_name = 'recordings/recording_confirm_delete.html'
    success_url   = reverse_lazy('recording_list')
 
class AnomalyListView(ListView):
    model               = AnomalyFlag
    template_name       = 'recordings/anomaly_list.html'
    context_object_name = 'anomalies'
 
    def get_queryset(self):
        return AnomalyFlag.objects.select_related('recording__species', 'flagged_by')
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_flags_count'] = self.get_queryset().filter(resolved=False).count()
        context['resolved_flags_count'] = self.get_queryset().filter(resolved=True).count()
        return context
 
class AnomalyCreateView(CreateView):
    model = AnomalyFlag
    form_class = AnomalyFlagForm
    template_name = 'recordings/anomaly_form.html'
    success_url = reverse_lazy('anomaly_list')

    def form_valid(self, form):
        recording = AudioRecording.objects.get(pk=self.kwargs['recording_pk'])

        flagged_by = None
        if self.request.user.is_authenticated:
            flagged_by = self.request.user

        recording.flag_as_anomaly(
            reason=form.cleaned_data['reason'],
            flagged_by=flagged_by,
        )

        return redirect(self.success_url)
 
 
class AnomalyUpdateView(UpdateView):
    model         = AnomalyFlag
    form_class    = AnomalyFlagForm
    template_name = 'recordings/anomaly_form.html'
    success_url   = reverse_lazy('anomaly_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        flag = self.object
        if flag.resolved:
            flag.recording.resolve_flags()
        return response
 
 
class AnomalyDeleteView(DeleteView):
    model = AnomalyFlag
    template_name = 'recordings/anomaly_confirm_delete.html'
    success_url = reverse_lazy('anomaly_list')

    def form_valid(self, form):
        recording = self.object.recording
        response = super().form_valid(form)

        if not recording.flags.exists():
            recording.is_anomaly = False
            recording.save(update_fields=['is_anomaly'])

        return response