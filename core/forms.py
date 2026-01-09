from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border rounded'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border rounded'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end:
            if end <= start:
                raise forms.ValidationError("End time must be after start time.")
