from django import forms
from django.contrib.auth.models import User
from .models import VolunteerProfile, EventManagerProfile, Event

class VolunteerSignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            VolunteerProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                age=self.data['age'],
                profession=self.data['profession'],
                gender=self.data['gender'],
                interests=self.data['interests'],
                pincode=self.data['pincode']
            )
        return user

class EventManagerSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            EventManagerProfile.objects.create(
                user=user,
                age=self.data['age'],
                phone_number=self.data['phone']
            )
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'type', 'address', 'pincode', 'date', 'time', 
                 'duration_hours', 'max_participants', 'image', 'latitude', 'longitude']
        
    def clean(self):
        cleaned_data = super().clean()
        duration_hours = cleaned_data.get('duration_hours')
        max_participants = cleaned_data.get('max_participants')
        
        if duration_hours:
            if duration_hours < 1 or duration_hours > 24:
                raise forms.ValidationError('Duration must be between 1 and 24 hours')
                
        if max_participants:
            if max_participants < 1 or max_participants > 1000:
                raise forms.ValidationError('Maximum participants must be between 1 and 1000')
        
        return cleaned_data
