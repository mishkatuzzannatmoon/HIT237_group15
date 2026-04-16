from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wildlife
from .forms import WildlifeForm


@login_required
def home(request):
    records = Wildlife.objects.filter(user=request.user).order_by('-observation_date')

    total_records = records.count()
    total_animals = sum(record.quantity for record in records)
    bird_count = records.filter(species='Bird').count()
    mammal_count = records.filter(species='Mammal').count()

    context = {
        'records': records,
        'total_records': total_records,
        'total_animals': total_animals,
        'bird_count': bird_count,
        'mammal_count': mammal_count,
    }
    return render(request, 'home.html', context)


@login_required
def wildlife_list(request):
    records = Wildlife.objects.filter(user=request.user).order_by('-observation_date')
    return render(request, 'wildlife_list.html', {'records': records})


@login_required
def add_wildlife(request):
    if request.method == 'POST':
        form = WildlifeForm(request.POST)
        if form.is_valid():
            wildlife = form.save(commit=False)
            wildlife.user = request.user
            wildlife.save()
            messages.success(request, 'Wildlife record added successfully.')
            return redirect('wildlife_list')
    else:
        form = WildlifeForm()

    return render(request, 'add_wildlife.html', {'form': form})


@login_required
def update_wildlife(request, wildlife_id):
    record = get_object_or_404(Wildlife, id=wildlife_id, user=request.user)

    if request.method == 'POST':
        form = WildlifeForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Wildlife record updated successfully.')
            return redirect('wildlife_list')
    else:
        form = WildlifeForm(instance=record)

    return render(request, 'update_wildlife.html', {'form': form, 'record': record})


@login_required
def delete_wildlife(request, wildlife_id):
    record = get_object_or_404(Wildlife, id=wildlife_id, user=request.user)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Wildlife record deleted successfully.')
        return redirect('wildlife_list')

    return render(request, 'delete_wildlife.html', {'record': record})