from django.shortcuts import redirect

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.views import View
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Species, AudioRecording, AnomalyFlag, ConservationStatus, RecordType
from .forms import SpeciesForm, AudioRecordingForm, AnomalyFlagForm, RegisterForm
from . import services

class SpeciesListView(ListView):
    model = Species
    template_name = 'recordings/species_list.html'
    context_object_name = 'species_list'


class SpeciesDetailView(DetailView):
    model = Species
    template_name = 'recordings/species_detail.html'


class SpeciesCreateView(LoginRequiredMixin, CreateView):
    model = Species
    form_class = SpeciesForm
    template_name = 'recordings/species_form.html'
    success_url = reverse_lazy('species_list')

    def form_valid(self, form):
        try:
            services.create_species(form.cleaned_data)
            messages.success(self.request, 'Species added successfully.')
            return redirect(self.success_url)
        except ValidationError as e:
            messages.error(self.request, str(e.message))
            return self.form_invalid(form)

class SpeciesUpdateView(LoginRequiredMixin, UpdateView):
    model = Species
    form_class = SpeciesForm
    template_name = 'recordings/species_form.html'
    success_url = reverse_lazy('species_list')


class SpeciesDeleteView(LoginRequiredMixin, DeleteView):
    model = Species
    template_name = 'recordings/species_confirm_delete.html'
    success_url = reverse_lazy('species_list')

class RecordingListView(ListView):
    model = AudioRecording
    template_name = 'recordings/recording_list.html'
    context_object_name = 'recordings'

    def get_queryset(self):
        return (
            AudioRecording.objects
            .with_details()
            .filter_by_params(self.request)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_species'] = Species.objects.order_by('common_name')
        context['conservation_choices'] = ConservationStatus.choices
        context['record_type_choices'] = RecordType.choices
        return context

class RecordingDetailView(DetailView):
    model = AudioRecording
    template_name = 'recordings/recording_detail.html'

    def get_queryset(self):
        return AudioRecording.objects.select_related('species', 'recorded_by').prefetch_related('flags')


class RecordingCreateView(LoginRequiredMixin, CreateView):
    model = AudioRecording
    form_class = AudioRecordingForm
    template_name = 'recordings/recording_form.html'
    success_url = reverse_lazy('recording_list')

    def form_valid(self, form):
        try:
            services.create_recording(
                user=self.request.user,
                form_data=form.cleaned_data,
            )
            messages.success(self.request, 'Recording submitted successfully.')
            return redirect(self.success_url)
        except ValidationError as e:
            messages.error(self.request, str(e.message))
            return self.form_invalid(form)


class RecordingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AudioRecording
    form_class = AudioRecordingForm
    template_name = 'recordings/recording_form.html'
    success_url = reverse_lazy('recording_list')

    def test_func(self):
        return self.request.user == self.get_object().recorded_by
 
    def handle_no_permission(self):
        messages.error(self.request, 'You can only edit your own recordings.')
        return redirect('recording_list')
 
    def form_valid(self, form):
        try:
            services.update_recording(
                user=self.request.user,
                recording=self.get_object(),
                form_data=form.cleaned_data,
            )
            messages.success(self.request, 'Recording updated successfully.')
            return redirect(self.success_url)
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)
        except ValidationError as e:
            messages.error(self.request, str(e.message))
            return self.form_invalid(form)


class RecordingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AudioRecording
    template_name = 'recordings/recording_confirm_delete.html'
    success_url = reverse_lazy('recording_list')

    def test_func(self):
        return self.request.user == self.get_object().recorded_by
 
    def handle_no_permission(self):
        messages.error(self.request, 'You can only delete your own recordings.')
        return redirect('recording_list')
 
    def form_valid(self, form):
        try:
            services.delete_recording(
                user=self.request.user,
                recording=self.get_object(),
            )
            messages.success(self.request, 'Recording deleted.')
            return redirect(self.success_url)
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)

        return response

class AnomalyListView(ListView):
    model = AnomalyFlag
    template_name = 'recordings/anomaly_list.html'
    context_object_name = 'anomalies'

    def get_queryset(self):
        return AnomalyFlag.objects.select_related('recording__species', 'flagged_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_flags_count'] = self.get_queryset().filter(resolved=False).count()
        context['resolved_flags_count'] = self.get_queryset().filter(resolved=True).count()
        return context

class AnomalyCreateView(LoginRequiredMixin, CreateView):
    model = AnomalyFlag
    form_class = AnomalyFlagForm
    template_name = 'recordings/anomaly_form.html'
    success_url = reverse_lazy('anomaly_list')

    def form_valid(self, form):
        try:
            recording = get_object_or_404(AudioRecording, pk=self.kwargs['recording_pk'])
            services.flag_recording(
                user=self.request.user,
                recording=recording,
                reason=form.cleaned_data['reason'],
            )
            messages.success(self.request, 'Recording flagged as anomaly.')
            return redirect(self.success_url)
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)
        except ValidationError as e: 
            messages.error(self.request, str(e.message))
            return self.form_invalid(form)

class AnomalyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AnomalyFlag
    form_class = AnomalyFlagForm
    template_name = 'recordings/anomaly_form.html'
    success_url = reverse_lazy('anomaly_list')

    def test_func(self):
        return self.request.user == self.get_object().flagged_by

    def handle_no_permission(self):
        messages.error(self.request, 'You can only edit your own anomaly flags.')
        return redirect('anomaly_list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            if self.object.resolved:
                services.resolve_flag(
                    user=self.request.user,
                    flag=self.object,
                )
                messages.success(self.request, 'Anomaly flag resolved.')
            return response
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)
        except ValidationError as e:
            messages.error(self.request, str(e.message))
            return self.form_invalid(form)

class AnomalyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AnomalyFlag
    template_name = 'recordings/anomaly_confirm_delete.html'
    success_url = reverse_lazy('anomaly_list')

    def test_func(self):
        return self.request.user == self.get_object().flagged_by

    def handle_no_permission(self):
        messages.error(self.request, 'You can only delete your own anomaly flags.')
        return redirect('anomaly_list')

    def form_valid(self, form):
        try:
            recording = self.object.recording
            response = super().form_valid(form)
            
            if not recording.flags.exists():
                recording.is_anomaly = False
                recording.save(update_fields=['is_anomaly'])
            
            messages.success(self.request, 'Anomaly flag deleted.')
            return response
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)

class RegisterView(View):

    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('recording_list')
        return render(request, self.template_name, {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('recording_list')
            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')
                return render(request, self.template_name, {'form': form})
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('login')
