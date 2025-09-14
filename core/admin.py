from django.contrib import admin
from .models import VolunteerProfile, EventManagerProfile, Event, EventFeedback

@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'age', 'profession', 'gender', 'pincode')
    search_fields = ('user__username', 'first_name', 'last_name', 'profession', 'pincode')
    list_filter = ('gender', 'age')
    
    fieldsets = (
        ('Personal Information', {
            'fields': (('first_name', 'last_name'), 'age', 'gender', 'profession')
        }),
        ('Contact Information', {
            'fields': ('address', 'pincode')
        }),
        ('Preferences', {
            'fields': ('interests',)
        }),
        ('Location Data', {
            'fields': (('latitude', 'longitude'),),
            'classes': ('collapse',)
        })
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(EventManagerProfile)
class EventManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'age')
    search_fields = ('user__username', 'phone_number')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'manager', 'date', 'time', 'duration_hours', 'max_participants', 'get_participant_count')
    search_fields = ('name', 'type', 'pincode')
    list_filter = ('type', 'date', 'duration_hours')
    list_editable = ('duration_hours', 'max_participants')  # Allow inline editing
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'manager', 'image')
        }),
        ('Event Capacity', {
            'fields': ('max_participants',),
            'description': 'Set maximum number of participants (1-1000)'
        }),
        ('Date and Time', {
            'fields': ('date', 'time', 'duration_hours'),
            'description': 'Event duration can be set between 1-24 hours'
        }),
        ('Location', {
            'fields': ('address', 'pincode', 'latitude', 'longitude')
        }),
        ('Participation', {
            'fields': ('participants', 'participation_requests'),
            'classes': ('collapse',)
        })
    )

    def get_participant_count(self, obj):
        return f"{obj.participants.count()}/{obj.max_participants}"
    get_participant_count.short_description = 'Participants (Current/Max)'

    def save_model(self, request, obj, form, change):
        # Validate max participants
        if obj.max_participants < 1:
            obj.max_participants = 1
        elif obj.max_participants > 1000:
            obj.max_participants = 1000
            
        # Validate duration hours
        if obj.duration_hours < 1:
            obj.duration_hours = 1
        elif obj.duration_hours > 24:
            obj.duration_hours = 24
            
        super().save_model(request, obj, form, change)

@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ('event', 'volunteer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('event__name', 'volunteer__username', 'comment')
    readonly_fields = ('created_at',)