from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='hostel_dashboard'),
    path('dashboard/', views.dashboard, name='hostel_dashboard_alt'),
    
    # API endpoints
    path('api/dashboard-data/', api_views.hostel_dashboard_data, name='hostel_dashboard_data'),
    path('api/statistics/', api_views.hostel_statistics, name='hostel_statistics'),
    
    # Hostel CRUD URLs
    path('hostels/', views.HostelListView.as_view(), name='hostel_list'),
    path('hostels/create/', views.HostelCreateView.as_view(), name='hostel_create'),
    path('hostels/<int:hostel_id>/', views.HostelDetailView.as_view(), name='hostel_detail'),
    path('hostels/<int:hostel_id>/update/', views.HostelUpdateView.as_view(), name='hostel_update'),
    path('hostels/<int:hostel_id>/delete/', views.HostelDeleteView.as_view(), name='hostel_delete'),
    
    # Room CRUD URLs
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/create/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:room_id>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('rooms/<int:room_id>/update/', views.RoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:room_id>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),
      # Allocation CRUD URLs
    path('allocations/', views.AllocationListView.as_view(), name='allocation_list'),
    path('allocations/create/', views.AllocationCreateView.as_view(), name='allocation_create'),
    path('allocations/allocate/', views.AllocationCreateView.as_view(), name='allocate_room'),
    path('allocations/<int:allocation_id>/', views.AllocationDetailView.as_view(), name='allocation_detail'),
    path('allocations/<int:allocation_id>/update/', views.AllocationUpdateView.as_view(), name='allocation_update'),
    path('allocations/<int:allocation_id>/vacate/', views.vacate_room, name='vacate_room'),
    
    # Student hostel history
    path('students/<int:student_id>/hostel-history/', views.student_hostel_history, name='student_hostel_history'),
]
