from django.urls import path
from .views import RecordingListView, RecordingDetailView, UploadRecordingView

urlpatterns = [
    path("", RecordingListView.as_view(), name="recording_list"),
    path("upload/", UploadRecordingView.as_view(), name="upload_recording"),
    path("<int:id>/", RecordingDetailView.as_view(), name="recording_detail"),
]