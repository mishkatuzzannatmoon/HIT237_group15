from django.db import models


class RecordingQuerySet(models.QuerySet):
    """
    Custom QuerySet for AudioRecording.

    """

    def high_confidence(self, threshold=0.8):
        return self.filter(confidence_score__gte=threshold)

    def medium_confidence(self):
        return self.filter(confidence_score__gte=0.5, confidence_score__lt=0.8)

    def low_confidence(self):
        return self.filter(confidence_score__lt=0.5)

    def anomalies(self):
        return self.filter(is_anomaly=True)

    def no_anomalies(self):
        """Recordings with no anomaly flag."""
        return self.filter(is_anomaly=False)

    def by_species(self, species_id):
        return self.filter(species_id=species_id)

    def by_conservation_status(self, status):
        return self.filter(species__conservation_status=status)

    def by_record_type(self, record_type):
        return self.filter(record_type=record_type)

    def from_date(self, date_from):
        return self.filter(recorded_at__date__gte=date_from)

    def to_date(self, date_to):
        return self.filter(recorded_at__date__lte=date_to)

    def with_details(self):
        return self.select_related('species', 'recorded_by')

    def filter_by_params(self, request):

        qs = self

        if request.GET.get('species'):
            qs = qs.by_species(request.GET.get('species'))

        if request.GET.get('conservation_status'):
            qs = qs.by_conservation_status(request.GET.get('conservation_status'))

        if request.GET.get('record_type'):
            qs = qs.by_record_type(request.GET.get('record_type'))

        if request.GET.get('date_from'):
            qs = qs.from_date(request.GET.get('date_from'))

        if request.GET.get('date_to'):
            qs = qs.to_date(request.GET.get('date_to'))

        confidence_map = {
            'high':   qs.high_confidence,
            'medium': qs.medium_confidence,
            'low':    qs.low_confidence,
        }
        if request.GET.get('confidence') in confidence_map:
            qs = confidence_map[request.GET.get('confidence')]()

        if request.GET.get('anomaly') == 'yes':
            qs = qs.anomalies()
        elif request.GET.get('anomaly') == 'no':
            qs = qs.no_anomalies()

        return qs


class RecordingManager(models.Manager):

    def get_queryset(self):
        return RecordingQuerySet(self.model, using=self._db)

    def high_confidence(self, threshold=0.8):
        return self.get_queryset().high_confidence(threshold)

    def medium_confidence(self):
        return self.get_queryset().medium_confidence()

    def low_confidence(self):
        return self.get_queryset().low_confidence()

    def anomalies(self):
        return self.get_queryset().anomalies()

    def with_details(self):
        return self.get_queryset().with_details()

    def filter_by_params(self, request):
        return self.get_queryset().filter_by_params(request)