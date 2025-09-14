from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import VolunteerProfile, EventManagerProfile, Event, RequestStatus, EventFeedback
from django.contrib.auth.decorators import login_required
from .forms import VolunteerSignupForm, EventManagerSignupForm, EventForm
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.db.models import F, Value, FloatField, ExpressionWrapper, Q, When, Case, BooleanField, Count
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from math import radians, cos, sin, asin, sqrt
import math
from django.db import IntegrityError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.conf import settings
import googlemaps

def index(request):
    return render(request, 'core/index.html')

def volunteer_signup(request):
    if request.method == 'POST':
        form = VolunteerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('volunteer_dashboard')
    else:
        form = VolunteerSignupForm()
    return render(request, 'core/volunteer_signup.html', {'form': form})

def volunteer_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('volunteer_dashboard')
    return render(request, 'core/volunteer_login.html')

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return round(c * r, 2)

@login_required
def volunteer_dashboard(request):
    events = Event.objects.select_related('manager').all()
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    # Get the current date and next day date
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Get volunteer profile and interests
    volunteer_profile = get_object_or_404(VolunteerProfile, user=request.user)
    user_interests = volunteer_profile.interests.lower().split(',') if volunteer_profile.interests else []
    user_interests = [interest.strip() for interest in user_interests]
    
    # Get volunteer location from profile
    user_lat = volunteer_profile.latitude
    user_lon = volunteer_profile.longitude
    
    current_datetime = timezone.now()
    # Get all upcoming events
    upcoming_events = Event.objects.filter(
        Q(date__gt=current_datetime.date()) |  # Future dates
        Q(date=current_datetime.date(), time__gt=current_datetime.time())  # Today but future time
    ).order_by('date', 'time')

    
    # Calculate distances if user has location
    if user_lat and user_lon:
        for event in upcoming_events:
            if event.latitude and event.longitude:
                # Get distance using Google Maps Distance Matrix API
                try:
                    distance_result = gmaps.distance_matrix(
                        origins=f"{user_lat},{user_lon}",
                        destinations=f"{event.latitude},{event.longitude}",
                        mode="driving",
                        units="metric"
                    )
                    
                    if distance_result['status'] == 'OK':
                        # Extract distance in kilometers
                        distance_text = distance_result['rows'][0]['elements'][0]['distance']['text']
                        distance_value = float(distance_text.replace(' km', ''))
                        event.distance = distance_value
                    else:
                        event.distance = None
                except Exception as e:
                    print(f"Error calculating distance: {e}")
                    event.distance = None
            else:
                event.distance = None
    else:
        for event in upcoming_events:
            event.distance = None
    
    # Prepare different priority categories with distance consideration
    tomorrow_events = []
    interest_events = []
    nearby_2km = []
    nearby_5km = []
    nearby_10km = []
    other_events = []
    completed_events = [] 
    
    for event in upcoming_events:
        # Check if event is happening tomorrow
        if event.date == tomorrow:
            tomorrow_events.append(event)
            continue

    for event in upcoming_events:
        # Check if event is completed
        if event.is_completed:
            completed_events.append(event)
            continue
            
        # Check if event matches user interests
        event_type_lower = event.type.lower()
        if any(interest in event_type_lower for interest in user_interests):
            interest_events.append(event)
            continue
            
        # Categorize by distance if available
        if hasattr(event, 'distance') and event.distance is not None:
            if event.distance <= 2:
                nearby_2km.append(event)
            elif event.distance <= 5:
                nearby_5km.append(event)
            elif event.distance <= 10:
                nearby_10km.append(event)
            else:
                other_events.append(event)
        else:
            other_events.append(event)
    
    # Sort each category by date
    for event_list in [tomorrow_events, interest_events, nearby_2km, nearby_5km, nearby_10km, other_events]:
        event_list.sort(key=lambda x: x.date)
    
    categorized_events = [
        {"category": "Happening Tomorrow", "events": tomorrow_events, "badge_class": "bg-danger"},
        {"category": "Matching Your Interests", "events": interest_events, "badge_class": "bg-success"},
        {"category": "Within 2km", "events": nearby_2km, "badge_class": "bg-primary"},
        {"category": "Within 5km", "events": nearby_5km, "badge_class": "bg-info"},
        {"category": "Within 10km", "events": nearby_10km, "badge_class": "bg-warning"},
        {"category": "Other Events", "events": other_events, "badge_class": "bg-secondary"}
    ]
    
    # Remove empty categories
    categorized_events = [cat for cat in categorized_events if cat["events"]]
    
    context = {
        'categorized_events': categorized_events,
        'user_interests': user_interests,
        'tomorrow': tomorrow,
        'has_location': bool(user_lat and user_lon),
        'current_datetime': current_datetime,  # Add current datetime to context
    }
    
    return render(request, 'core/volunteer_dashboard.html', context)

def manager_signup(request):
    if request.method == 'POST':
        form = EventManagerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('manager_dashboard')
    else:
        form = EventManagerSignupForm()
    return render(request, 'core/manager_signup.html', {'form': form})

def manager_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('manager_dashboard')
    return render(request, 'core/manager_login.html')

@login_required
def manager_dashboard(request):
    # Get events managed by the logged-in user
    managed_events = Event.objects.filter(manager=request.user).prefetch_related(
        'event_feedbacks',
        'event_feedbacks__volunteer',
        'participants'
    )

    upcoming_events = managed_events.filter(date__gte=timezone.now().date())
    past_events = managed_events.filter(date__lt=timezone.now().date())

    context = {
        'managed_events': managed_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'core/manager_dashboard.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        
        # Round latitude and longitude to 6 decimal places
        if 'latitude' in request.POST and 'longitude' in request.POST:
            try:
                lat = round(float(request.POST['latitude']), 6)
                lng = round(float(request.POST['longitude']), 6)
                # Create a copy of POST data to modify
                post_data = request.POST.copy()
                post_data['latitude'] = str(lat)
                post_data['longitude'] = str(lng)
                # Update form with rounded coordinates
                form = EventForm(post_data, request.FILES)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid coordinates provided')
                return render(request, 'core/create_event.html', {'form': form})

        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.manager = EventManagerProfile.objects.get(user=request.user)
                event.save()
                messages.success(request, 'Event created successfully!')
                return redirect('manager_dashboard')
            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
                print(f"Error creating event: {str(e)}")
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form errors:", form.errors)
    else:
        form = EventForm()
    
    return render(request, 'core/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)
            
            # Update latitude and longitude
            updated_event.latitude = request.POST.get('latitude')
            updated_event.longitude = request.POST.get('longitude')
            
            updated_event.save()
            return redirect('manager_dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'core/edit_event.html', {'form': form, 'event': event})

@login_required
def past_events(request):
    events = Event.objects.filter(date__lt='2024-01-01').order_by('-date')
    return render(request, 'core/past_events.html', {'events': events})

def user_logout(request):
    logout(request)
    return redirect('index')

def participate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if event is full
    if event.participants.count() >= event.max_participants:
        messages.error(request, "Sorry, this event is already full.")
        return redirect('volunteer_dashboard')
    
    # Rest of your existing participation logic
    if request.user not in event.participants.all():
        event.participation_requests.add(request.user)
        messages.success(request, "Participation request sent successfully!")
    else:
        messages.info(request, "You are already registered for this event.")
    
    return redirect('volunteer_dashboard')

@login_required
def my_events(request):
    user = request.user
    participated_events = Event.objects.filter(
        participants=user
    ).order_by('-date')
    
    requested_events = Event.objects.filter(
        participation_requests=user
    ).order_by('-date')
    
    # Update event completion status
    today = date.today()
    for event in participated_events:
        if event.date < today and not event.is_completed:
            event.is_completed = True
            event.completion_date = event.date
            event.save()

    context = {
        'participated_events': participated_events,
        'requested_events': requested_events,
    }
    return render(request, 'core/my_events.html', context)

@login_required
@ensure_csrf_cookie
def save_user_location(request):
    if request.method == 'POST':
        try:
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                volunteer_profile = request.user.volunteerprofile
                # Store the new location
                volunteer_profile.latitude = latitude
                volunteer_profile.longitude = longitude
                # Add timestamp for ML purposes
                volunteer_profile.last_location_update = timezone.now()
                volunteer_profile.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Location updated successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Invalid coordinates'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error', 
        'message': 'Invalid request method'
    }, status=405)

@login_required
def manage_requests(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Filter out deleted users
    requests = [user for user in event.participation_requests.all() if user is not None]
    approved_requests = [status for status in event.participants.through.objects.filter(event=event) if status.user is not None]
    rejected_requests = [status for status in event.rejected_requests.through.objects.filter(event=event) if status.user is not None]

    context = {
        'event': event,
        'requests': requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'core/manage_requests.html', context)

@login_required
def download_certificate(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    volunteer_profile = request.user.volunteerprofile
    
    if request.user not in event.participants.all():
        messages.error(request, "You haven't participated in this event.")
        return redirect('my_events')
    
    full_name = f"{volunteer_profile.first_name} {volunteer_profile.last_name}"
    
    return JsonResponse({
        'status': 'success',
        'event_name': event.name,
        'date': event.date.strftime('%B %d, %Y'),
        'volunteer_name': full_name,
        'event_type': event.type
    })

def events_list(request):
    today = timezone.now().date()
    
    events = Event.objects.annotate(
        is_past=ExpressionWrapper(Q(date__lt=today), output_field=BooleanField()),
        participant_count=Count('participants'),
        participation_percentage=Case(
            When(max_participants__gt=0, 
                 then=ExpressionWrapper(
                     100.0 * Count('participants') / F('max_participants'),
                     output_field=FloatField()
                 )),
            default=Value(0),
            output_field=FloatField(),
        )
    ).prefetch_related('participants')
    
    context = {
        'events': events,
        'upcoming_events': events.filter(date__gte=today),
        'past_events': events.filter(date__lt=today),
    }
    
    return render(request, 'core/events_list.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event,
        'participant_count': event.participants.count(),
        'is_participant': request.user in event.participants.all(),
        'has_pending_request': request.user in event.participation_requests.all(),
        'is_past': event.date < timezone.now().date(),
        'participation_percentage': (
            (event.participants.count() / event.max_participants * 100)
            if event.max_participants else 0
        )
    }
    
    return render(request, 'core/event_detail.html', context)

@login_required
def approve_participant(request, event_id, user_id):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(User, id=user_id)
    
    # Check if there's still space
    if event.participants.count() >= event.max_participants:
        messages.error(request, "Cannot approve request. Event is already full.")
        return redirect('manager_dashboard')
    
    # Rest of your approval logic
    event.participation_requests.remove(user)
    event.participants.add(user)
    messages.success(request, f"Approved participation request for {user.username}")
    
    return redirect('manager_dashboard')

@login_required
def approve_request(request, event_id, user_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        user = get_object_or_404(User, id=user_id)
        
        # Verify that the logged-in user is the event manager
        if request.user != event.manager.user:
            messages.error(request, "You don't have permission to manage this event.")
            return redirect('manage_requests', event_id=event_id)
        
        # Check if there's still space in the event
        if event.participants.count() >= event.max_participants:
            messages.error(request, "Cannot approve request. Event is already full.")
            return redirect('manage_requests', event_id=event_id)
        
        try:
            # Remove from requests and add to participants
            event.participation_requests.remove(user)
            event.participants.add(user)
            
            # Create request status record
            RequestStatus.objects.create(
                event=event,
                user=user,
                manager=event.manager,
                status='APPROVED'
            )
            
            messages.success(request, f"Approved participation request for {user.username}")
        except Exception as e:
            messages.error(request, f"Error approving request: {str(e)}")
            
    return redirect('manage_requests', event_id=event_id)

@login_required
def reject_request(request, event_id, user_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        user = get_object_or_404(User, id=user_id)
        
        # Verify that the logged-in user is the event manager
        if request.user != event.manager.user:
            messages.error(request, "You don't have permission to manage this event.")
            return redirect('manage_requests', event_id=event_id)
        
        try:
            # Remove from requests and add to rejected
            event.participation_requests.remove(user)
            event.rejected_requests.add(user)
            
            # Create request status record
            RequestStatus.objects.create(
                event=event,
                user=user,
                manager=event.manager,
                status='REJECTED'
            )
            
            messages.success(request, f"Rejected participation request for {user.username}")
        except Exception as e:
            messages.error(request, f"Error rejecting request: {str(e)}")
            
    return redirect('manage_requests', event_id=event_id)

@login_required
def submit_feedback(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        # Check if user already submitted feedback
        if EventFeedback.objects.filter(event=event, volunteer=request.user).exists():
            messages.error(request, 'You have already submitted feedback for this event.')
            return redirect('my_events')
        
        # Create new feedback
        EventFeedback.objects.create(
            event=event,
            volunteer=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('my_events')
    
    return redirect('my_events')