from django.shortcuts import render

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

def recording_list(request):
    return render(request, 'recordings/recording_list.html', {"recordings": recordings_data})

def upload_recording(request):
    return render(request, 'recordings/upload_recording.html')

def recording_detail(request, id):
    selected = None
    for recording in recordings_data:
        if recording["id"] == id:
            selected = recording
            break
    return render(request, 'recordings/recording_detail.html', {"recording": selected})