from django.contrib import admin
from .models import Hostel, Room, HostelAllocation

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('hostel_id', 'hostel_name', 'warden_name', 'contact_number', 'total_rooms')
    search_fields = ('hostel_name', 'warden_name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'hostel', 'room_number', 'capacity', 'status')
    list_filter = ('status', 'hostel', 'capacity')
    search_fields = ('room_number', 'hostel__hostel_name')
    list_editable = ('status',)

@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ('allocation_id', 'student', 'room', 'allocation_date', 'is_active')
    list_filter = ('is_active', 'allocation_date', 'room__hostel')
    search_fields = ('student__name', 'room__room_number')
    date_hierarchy = 'allocation_date'
