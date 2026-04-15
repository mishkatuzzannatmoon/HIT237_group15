from django.shortcuts import render
from django.views import View

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
