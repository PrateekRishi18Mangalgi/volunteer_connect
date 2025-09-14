from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from decimal import Decimal

class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField()
    profession = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    interests = models.TextField()
    pincode = models.CharField(max_length=10)
    address= models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class EventManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=200,blank=True)  # Add this field
    phone_number = models.CharField(max_length=20)
    age = models.IntegerField()
    
    class Meta:
        verbose_name = 'Event Manager Profile'
        verbose_name_plural = 'Event Manager Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.organization_name}"

    def clean(self):
        # Add validation
        if self.age < 18:
            raise ValidationError({'age': 'Manager must be at least 18 years old'})
        
        # Validate phone number format
        if not re.match(r'^\+?1?\d{9,15}$', self.phone_number):
            raise ValidationError({'phone_number': 'Invalid phone number format'})

class Event(models.Model):
    manager = models.ForeignKey(
        'auth.User',  # Change from EventManagerProfile to auth.User
        on_delete=models.CASCADE,
        related_name='managed_events'
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    image = models.ImageField(upload_to='event_images/')
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[DecimalValidator(9, 6)],
        null=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[DecimalValidator(9, 6)],
        null=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='participated_events',
        blank=True
    )
    participation_requests = models.ManyToManyField(
        User,
        related_name='requested_events',
        blank=True
    )
    rejected_requests = models.ManyToManyField(
        User,
        related_name='rejected_events',
        blank=True
    )
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=50)
    duration_hours = models.PositiveIntegerField(
        default=1,
        help_text="Duration of the event in hours",
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )

    def save(self, *args, **kwargs):
        # Round coordinates before saving
        if self.latitude:
            self.latitude = Decimal(str(round(float(self.latitude), 6)))
        if self.longitude:
            self.longitude = Decimal(str(round(float(self.longitude), 6)))
        super().save(*args, **kwargs)

class RequestStatus(models.Model):
    EVENT_REQUEST_STATUS = [
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(EventManagerProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=EVENT_REQUEST_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Request Status'
        verbose_name_plural = 'Request Statuses'
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.name} - {self.status}"

class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_feedbacks')  # Changed from 'feedbacks'
    volunteer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='given_feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'volunteer']
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.volunteer.username} for {self.event.name}"
