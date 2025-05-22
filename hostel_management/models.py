from django.db import models

class Hostel(models.Model):
    hostel_id = models.AutoField(primary_key=True)
    hostel_name = models.CharField(max_length=100)
    warden_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    total_rooms = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.hostel_name

class Room(models.Model):
    ROOM_STATUS = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    )
    
    room_id = models.AutoField(primary_key=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    capacity = models.IntegerField(default=2)
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('hostel', 'room_number')
    
    def __str__(self):
        return f"{self.hostel.hostel_name} - Room {self.room_number}"

class HostelAllocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    student = models.OneToOneField('student_management.Student', on_delete=models.CASCADE, related_name='hostel_allocation')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.room.room_number}"
