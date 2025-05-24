from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from .models import Hostel, Room, HostelAllocation
from .forms import HostelForm, RoomForm, HostelAllocationForm, HostelSearchForm, RoomSearchForm, AllocationSearchForm
from student_management.models import Student

@login_required
def dashboard(request):
    # Get hostel statistics
    total_hostels = Hostel.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    total_allocations = HostelAllocation.objects.filter(is_active=True).count()
    
    # Get recent allocations
    recent_allocations = HostelAllocation.objects.all().order_by('-created_at')[:5]
    
    # Hostel occupancy data for chart
    hostels = Hostel.objects.all()
    hostel_data = []
    
    for hostel in hostels:
        total_hostel_rooms = Room.objects.filter(hostel=hostel).count()
        occupied_hostel_rooms = Room.objects.filter(hostel=hostel, status='occupied').count()
        occupancy_rate = 0
        if total_hostel_rooms > 0:
            occupancy_rate = (occupied_hostel_rooms / total_hostel_rooms) * 100
        
        hostel_data.append({
            'name': hostel.hostel_name,
            'total_rooms': total_hostel_rooms,
            'occupied_rooms': occupied_hostel_rooms,
            'occupancy_rate': occupancy_rate
        })
    
    context = {
        'total_hostels': total_hostels,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'total_allocations': total_allocations,
        'recent_allocations': recent_allocations,
        'hostel_data': hostel_data,
    }
    
    return render(request, 'hostel_management/dashboard.html', context)

# Hostel CRUD views
class HostelListView(LoginRequiredMixin, ListView):
    model = Hostel
    template_name = 'hostel_management/hostel_list.html'
    context_object_name = 'hostels'
    paginate_by = 10
    ordering = ['hostel_id']  # Add ordering to avoid UnorderedObjectListWarning
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = HostelSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            if search_query:
                queryset = queryset.filter(
                    Q(hostel_name__icontains=search_query) | 
                    Q(warden_name__icontains=search_query)
                )
        
        # Add room count to each hostel
        queryset = queryset.annotate(room_count=Count('rooms'))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = HostelSearchForm(self.request.GET)
        return context

class HostelDetailView(LoginRequiredMixin, DetailView):
    model = Hostel
    template_name = 'hostel_management/hostel_detail.html'
    context_object_name = 'hostel'
    pk_url_kwarg = 'hostel_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hostel = self.get_object()
        
        # Get rooms in this hostel
        rooms = Room.objects.filter(hostel=hostel)
        available_rooms = rooms.filter(status='available').count()
        occupied_rooms = rooms.filter(status='occupied').count()
        maintenance_rooms = rooms.filter(status='maintenance').count()
        
        context['rooms'] = rooms
        context['available_rooms'] = available_rooms
        context['occupied_rooms'] = occupied_rooms
        context['maintenance_rooms'] = maintenance_rooms
        
        return context

class HostelCreateView(LoginRequiredMixin, CreateView):
    model = Hostel
    form_class = HostelForm
    template_name = 'hostel_management/hostel_form.html'
    success_url = reverse_lazy('hostel_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Hostel'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Hostel created successfully.')
        return super().form_valid(form)

class HostelUpdateView(LoginRequiredMixin, UpdateView):
    model = Hostel
    form_class = HostelForm
    template_name = 'hostel_management/hostel_form.html'
    pk_url_kwarg = 'hostel_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Hostel'
        return context
    
    def get_success_url(self):
        return reverse_lazy('hostel_detail', kwargs={'hostel_id': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Hostel updated successfully.')
        return super().form_valid(form)

class HostelDeleteView(LoginRequiredMixin, DeleteView):
    model = Hostel
    template_name = 'hostel_management/hostel_confirm_delete.html'
    success_url = reverse_lazy('hostel_list')
    pk_url_kwarg = 'hostel_id'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Hostel deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Room CRUD views
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'hostel_management/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 10
    ordering = ['room_id']  # Add ordering to avoid UnorderedObjectListWarning
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = RoomSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            hostel = form.cleaned_data.get('hostel')
            status = form.cleaned_data.get('status')
            capacity = form.cleaned_data.get('capacity')
            
            if search_query:
                queryset = queryset.filter(room_number__icontains=search_query)
                
            if hostel:
                queryset = queryset.filter(hostel=hostel)
                
            if status:
                queryset = queryset.filter(status=status)
                
            if capacity:
                queryset = queryset.filter(capacity=capacity)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = RoomSearchForm(self.request.GET)
        return context

class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    template_name = 'hostel_management/room_detail.html'
    context_object_name = 'room'
    pk_url_kwarg = 'room_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        
        # Get allocations for this room
        allocations = HostelAllocation.objects.filter(room=room).order_by('-is_active', '-allocation_date')
        context['allocations'] = allocations
        
        return context

class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hostel_management/room_form.html'
    success_url = reverse_lazy('room_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Room'
        
        # If we got a hostel_id parameter, pre-select that hostel
        hostel_id = self.request.GET.get('hostel_id')
        if hostel_id:
            initial_data = self.get_form_kwargs().get('initial', {})
            initial_data['hostel'] = hostel_id
            self.get_form_kwargs()['initial'] = initial_data
        
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Room created successfully.')
        return super().form_valid(form)

class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hostel_management/room_form.html'
    pk_url_kwarg = 'room_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Room'
        return context
    
    def get_success_url(self):
        return reverse_lazy('room_detail', kwargs={'room_id': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Room updated successfully.')
        return super().form_valid(form)

class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'hostel_management/room_confirm_delete.html'
    success_url = reverse_lazy('room_list')
    pk_url_kwarg = 'room_id'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Room deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Allocation CRUD views
class AllocationListView(LoginRequiredMixin, ListView):
    model = HostelAllocation
    template_name = 'hostel_management/allocation_list.html'
    context_object_name = 'allocations'
    paginate_by = 10
    ordering = ['allocation_id']  # Add ordering to avoid UnorderedObjectListWarning
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = AllocationSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            hostel = form.cleaned_data.get('hostel')
            status = form.cleaned_data.get('status')
            allocation_date_start = form.cleaned_data.get('allocation_date_start')
            allocation_date_end = form.cleaned_data.get('allocation_date_end')
            
            if search_query:
                queryset = queryset.filter(student__name__icontains=search_query)
            
            if hostel:
                queryset = queryset.filter(room__hostel=hostel)
                
            if status:
                is_active = status == 'True'
                queryset = queryset.filter(is_active=is_active)
                
            if allocation_date_start:
                queryset = queryset.filter(allocation_date__gte=allocation_date_start)
                
            if allocation_date_end:
                queryset = queryset.filter(allocation_date__lte=allocation_date_end)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AllocationSearchForm(self.request.GET)
        return context

class AllocationDetailView(LoginRequiredMixin, DetailView):
    model = HostelAllocation
    template_name = 'hostel_management/allocation_detail.html'
    context_object_name = 'allocation'
    pk_url_kwarg = 'allocation_id'

class AllocationCreateView(LoginRequiredMixin, CreateView):
    model = HostelAllocation
    form_class = HostelAllocationForm
    template_name = 'hostel_management/allocation_form.html'
    success_url = reverse_lazy('allocation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Allocate Room'
        return context
    
    def form_valid(self, form):
        allocation = form.save(commit=False)
        
        # Update the room status to occupied when allocated
        room = allocation.room
        room.status = 'occupied'
        room.save()
        
        messages.success(self.request, 'Room allocated successfully.')
        return super().form_valid(form)

class AllocationUpdateView(LoginRequiredMixin, UpdateView):
    model = HostelAllocation
    form_class = HostelAllocationForm
    template_name = 'hostel_management/allocation_form.html'
    pk_url_kwarg = 'allocation_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Allocation'
        return context
    
    def get_success_url(self):
        return reverse_lazy('allocation_detail', kwargs={'allocation_id': self.object.pk})
    
    def form_valid(self, form):
        allocation = form.save(commit=False)
        
        # Update room status based on is_active
        old_allocation = HostelAllocation.objects.get(pk=allocation.pk)
        if old_allocation.is_active and not allocation.is_active:
            # Freeing up the room
            room = allocation.room
            room.status = 'available'
            room.save()
        elif not old_allocation.is_active and allocation.is_active:
            # Re-occupying the room
            room = allocation.room
            room.status = 'occupied'
            room.save()
            
        messages.success(self.request, 'Allocation updated successfully.')
        return super().form_valid(form)

@login_required
def vacate_room(request, allocation_id):
    allocation = get_object_or_404(HostelAllocation, pk=allocation_id)
    
    if request.method == 'POST':
        # Mark allocation as inactive
        allocation.is_active = False
        allocation.save()
        
        # Update room status to available
        room = allocation.room
        room.status = 'available'
        room.save()
        
        messages.success(request, f"{allocation.student.name} has vacated room {allocation.room.room_number}.")
        return redirect('allocation_list')
        
    return render(request, 'hostel_management/vacate_room_confirm.html', {'allocation': allocation})

@login_required
def student_hostel_history(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    allocations = HostelAllocation.objects.filter(student=student).order_by('-allocation_date')
    
    context = {
        'student': student,
        'allocations': allocations
    }
    
    return render(request, 'hostel_management/student_hostel_history.html', context)

@login_required
def hostel_report(request):
    """View for generating and displaying hostel occupancy and allocation reports"""
    hostels = Hostel.objects.all().annotate(
        total_rooms=Count('rooms'),
        occupied_rooms=Count('rooms', filter=Q(rooms__status='occupied')),
        available_rooms=Count('rooms', filter=Q(rooms__status='available')),
        maintenance_rooms=Count('rooms', filter=Q(rooms__status='maintenance'))
    )
    
    # Get overall statistics
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    available_rooms = Room.objects.filter(status='available').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    
    # Calculate occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Get recent allocations
    recent_allocations = HostelAllocation.objects.filter(
        is_active=True
    ).order_by('-allocation_date')[:10]
    
    context = {
        'hostels': hostels,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': occupancy_rate,
        'recent_allocations': recent_allocations,
    }
    
    return render(request, 'hostel_management/hostel_report.html', context)
