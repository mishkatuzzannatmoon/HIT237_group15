from django.contrib import admin

from .models import Species, Location, Recording, Anomaly

admin.site.register(Species)
admin.site.register(Location)
admin.site.register(Recording)
admin.site.register(Anomaly)
