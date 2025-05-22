from django import forms
from .models import Hostel, Room, HostelAllocation
from student_management.models import Student

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ('hostel_name', 'warden_name', 'contact_number', 'total_rooms')
        widgets = {
            'hostel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'warden_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('hostel', 'room_number', 'capacity', 'status')
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class HostelAllocationForm(forms.ModelForm):
    class Meta:
        model = HostelAllocation
        fields = ('student', 'room', 'end_date', 'is_active')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(HostelAllocationForm, self).__init__(*args, **kwargs)
        # Only show rooms that are available
        self.fields['room'].queryset = Room.objects.filter(status='available')
        # Only show students who don't have an active room allocation
        allocated_students = HostelAllocation.objects.filter(is_active=True).values_list('student', flat=True)
        self.fields['student'].queryset = Student.objects.exclude(student_id__in=allocated_students)
        
        # If this is an edit form, include the current student in the queryset
        if self.instance and self.instance.pk:
            self.fields['student'].queryset |= Student.objects.filter(pk=self.instance.student.pk)
            # If editing an existing allocation, include the current room in choices
            self.fields['room'].queryset |= Room.objects.filter(pk=self.instance.room.pk)

class HostelSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Hostel Name or Warden'})
    )

class RoomSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Room Number'})
    )
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Hostels"    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Room.ROOM_STATUS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    capacity = forms.ChoiceField(
        choices=[('', 'All Capacities')] + [(i, i) for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AllocationSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Student Name'})
    )
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Hostels"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('True', 'Active'), ('False', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    allocation_date_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    allocation_date_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
