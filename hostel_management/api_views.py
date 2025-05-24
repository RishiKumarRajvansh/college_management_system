from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Hostel, Room, HostelAllocation
from student_management.models import Student

def hostel_dashboard_data(request):
    """API endpoint for hostel management dashboard data"""
    try:
        # Room status distribution
        room_status_data = []
        for status, label in Room.ROOM_STATUS:
            count = Room.objects.filter(status=status).count()
            room_status_data.append({'status': label, 'count': count})
        
        # Hostel-wise occupancy
        hostel_occupancy = []
        hostels = Hostel.objects.all()
        for hostel in hostels:
            total_rooms = Room.objects.filter(hostel=hostel).count()
            occupied_rooms = Room.objects.filter(hostel=hostel, status='occupied').count()
            occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            hostel_occupancy.append({
                'hostel_name': hostel.hostel_name,
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'occupancy_rate': round(occupancy_rate, 2)
            })
        
        # Monthly allocations (last 12 months)
        monthly_allocations = []
        today = timezone.now().date()
        for i in range(12):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = HostelAllocation.objects.filter(
                allocation_date__range=[month_start, month_end]
            ).count()
            
            monthly_allocations.append({
                'month': month_start.strftime('%b %Y'),
                'allocations': count
            })
        
        monthly_allocations.reverse()
        
        # Room capacity utilization
        capacity_data = []
        rooms_with_capacity = Room.objects.values('capacity').annotate(
            room_count=Count('room_id'),
            occupied_count=Count('room_id', filter=Q(status='occupied'))
        )
        
        for item in rooms_with_capacity:
            capacity = item['capacity']
            total_rooms = item['room_count']
            occupied_rooms = item['occupied_count']
            utilization = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            capacity_data.append({
                'capacity': f"{capacity} Seater",
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'utilization': round(utilization, 2)
            })
        
        # Recent allocation trends (last 30 days)
        allocation_trends = []
        for i in range(30):
            date = today - timedelta(days=i)
            new_allocations = HostelAllocation.objects.filter(allocation_date=date).count()
            vacated_allocations = HostelAllocation.objects.filter(
                end_date=date,
                is_active=False
            ).count()
            allocation_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'new_allocations': new_allocations,
                'vacated': vacated_allocations
            })
        
        allocation_trends.reverse()
        
        # Gender-wise allocation (if gender field exists in Student model)
        gender_distribution = []
        try:
            if hasattr(Student, 'gender'):
                for gender in ['Male', 'Female', 'Other']:
                    count = HostelAllocation.objects.filter(
                        student__gender=gender,
                        is_active=True
                    ).count()
                    if count > 0:
                        gender_distribution.append({'gender': gender, 'count': count})
        except:
            # Handle case where gender field might not exist
            active_allocations = HostelAllocation.objects.filter(is_active=True).count()
            if active_allocations > 0:
                gender_distribution.append({'gender': 'Not Specified', 'count': active_allocations})
            else:
                gender_distribution = []
        
        return JsonResponse({
            'success': True,
            'data': {
                'room_status': room_status_data,
                'hostel_occupancy': hostel_occupancy,
                'monthly_allocations': monthly_allocations,
                'capacity_utilization': capacity_data,
                'allocation_trends': allocation_trends,
                'gender_distribution': gender_distribution
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def hostel_statistics(request):
    """API endpoint for hostel statistics"""
    try:
        # Basic statistics
        total_hostels = Hostel.objects.count()
        total_rooms = Room.objects.count()
        available_rooms = Room.objects.filter(status='available').count()
        occupied_rooms = Room.objects.filter(status='occupied').count()
        maintenance_rooms = Room.objects.filter(status='maintenance').count()
        
        # Allocation statistics
        total_allocations = HostelAllocation.objects.count()
        active_allocations = HostelAllocation.objects.filter(is_active=True).count()
        
        # Capacity statistics
        total_capacity = Room.objects.aggregate(
            total=Count('capacity')
        )['total'] or 0
        
        # Occupancy rate
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        # Average room capacity
        avg_capacity = Room.objects.aggregate(
            avg=Avg('capacity')
        )['avg'] or 0
        
        # Students with accommodation
        total_students = Student.objects.count()
        accommodated_students = active_allocations
        accommodation_rate = (accommodated_students / total_students * 100) if total_students > 0 else 0
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_hostels': total_hostels,
                'total_rooms': total_rooms,
                'available_rooms': available_rooms,
                'occupied_rooms': occupied_rooms,
                'maintenance_rooms': maintenance_rooms,
                'occupancy_rate': round(occupancy_rate, 2),
                'total_allocations': total_allocations,
                'active_allocations': active_allocations,
                'total_capacity': total_capacity,
                'avg_capacity': round(float(avg_capacity), 2),
                'total_students': total_students,
                'accommodated_students': accommodated_students,
                'accommodation_rate': round(accommodation_rate, 2)
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)