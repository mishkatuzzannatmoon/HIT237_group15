from django.urls import path
from . import views

urlpatterns = [
    path('', views.recording_list, name='recording_list'),
    path('upload/', views.upload_recording, name='upload_recording'),
    path('<int:id>/', views.recording_detail, name='recording_detail'),
]