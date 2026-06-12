from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q, Sum
from .models import FeeCategory, FeeStructure, Payment
from .forms import FeeCategoryForm, FeeStructureForm, PaymentForm, FeeCategorySearchForm
from student_management.models import Student


class FeeDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view for Fee Management module"""
    template_name = 'fee_management/dashboard.html'
    model = Payment
    context_object_name = 'recent_payments'
    
    def get_queryset(self):
        return Payment.objects.order_by('-payment_date')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_fees_collected'] = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        context['pending_payments'] = Payment.objects.filter(status='pending').count()
        context['fee_categories'] = FeeCategory.objects.count()
        context['fee_structures'] = FeeStructure.objects.count()
        return context


# Fee Category Views
class FeeCategoryListView(LoginRequiredMixin, ListView):
    """View for listing all fee categories"""
    model = FeeCategory
    template_name = 'fee_management/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    def get_queryset(self):
        search_form = FeeCategorySearchForm(self.request.GET)
        queryset = FeeCategory.objects.all().order_by('name')
        
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = FeeCategorySearchForm(self.request.GET)
        return context


class FeeCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new fee category"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fee_management/category_form.html'
    success_url = reverse_lazy('fee_category_list')
    success_message = "Fee category '%(name)s' was created successfully"


class FeeCategoryDetailView(LoginRequiredMixin, DetailView):
    """View for showing fee category details"""
    model = FeeCategory
    template_name = 'fee_management/category_detail.html'
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['fee_structures'] = FeeStructure.objects.filter(category=category)
        return context


class FeeCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an existing fee category"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fee_management/category_form.html'
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    success_message = "Fee category '%(name)s' was updated successfully"
    
    def get_success_url(self):
        return reverse('fee_category_detail', kwargs={'category_id': self.object.fee_category_id})


class FeeCategoryDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a fee category"""
    model = FeeCategory
    template_name = 'fee_management/category_confirm_delete.html'
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    success_url = reverse_lazy('fee_category_list')
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f"Fee category '{category.name}' was deleted successfully")
        return super().delete(request, *args, **kwargs)


# Fee Structure Views
class FeeStructureListView(LoginRequiredMixin, ListView):
    """View for listing all fee structures"""
    model = FeeStructure
    template_name = 'fee_management/structure_list.html'
    context_object_name = 'structures'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = FeeStructure.objects.all().order_by('-academic_year', 'category__name')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(category__name__icontains=search_query) |
                Q(course__name__icontains=search_query)
            )
            
        # Apply academic year filter if provided
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get unique academic years for filter dropdown
        academic_years = FeeStructure.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        context['academic_years'] = academic_years
        
        return context


class FeeStructureCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new fee structure"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fee_management/structure_form.html'
    success_url = reverse_lazy('fee_structure_list')
    success_message = "Fee structure for '%(course)s' was created successfully"


class FeeStructureDetailView(LoginRequiredMixin, DetailView):
    """View for showing fee structure details"""
    model = FeeStructure
    template_name = 'fee_management/structure_detail.html'
    context_object_name = 'structure'
    pk_url_kwarg = 'structure_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        structure = self.get_object()
        context['payments'] = Payment.objects.filter(fee_structure=structure)
        return context


class FeeStructureUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an existing fee structure"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fee_management/structure_form.html'
    context_object_name = 'structure'
    pk_url_kwarg = 'structure_id'
    success_message = "Fee structure was updated successfully"
    
    def get_success_url(self):
        return reverse('fee_structure_detail', kwargs={'structure_id': self.object.fee_structure_id})


class FeeStructureDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a fee structure"""
    model = FeeStructure
    template_name = 'fee_management/structure_confirm_delete.html'
    context_object_name = 'structure'
    pk_url_kwarg = 'structure_id'
    success_url = reverse_lazy('fee_structure_list')
    
    def delete(self, request, *args, **kwargs):
        structure = self.get_object()
        messages.success(request, f"Fee structure for '{structure.course}' was deleted successfully")
        return super().delete(request, *args, **kwargs)


# Payment Views
class PaymentListView(LoginRequiredMixin, ListView):
    """View for listing all payments"""
    model = Payment
    template_name = 'fee_management/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Payment.objects.all().order_by('-payment_date')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(receipt_number__icontains=search_query)
            )
            
        # Apply status filter if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Apply payment method filter if provided
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)
            
        return queryset


class PaymentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new payment"""
    model = Payment
    form_class = PaymentForm
    template_name = 'fee_management/payment_form.html'
    success_url = reverse_lazy('payment_list')
    success_message = "Payment was recorded successfully"


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """View for showing payment details"""
    model = Payment
    template_name = 'fee_management/payment_detail.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'


class PaymentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an existing payment"""
    model = Payment
    form_class = PaymentForm
    template_name = 'fee_management/payment_form.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'
    success_message = "Payment was updated successfully"
    
    def get_success_url(self):
        return reverse('payment_detail', kwargs={'payment_id': self.object.payment_id})


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a payment"""
    model = Payment
    template_name = 'fee_management/payment_confirm_delete.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'
    success_url = reverse_lazy('payment_list')
    
    def delete(self, request, *args, **kwargs):
        payment = self.get_object()
        messages.success(request, f"Payment #{payment.receipt_number} was deleted successfully")
        return super().delete(request, *args, **kwargs)


class StudentFeeView(LoginRequiredMixin, DetailView):
    """View for showing all fees and payments for a specific student"""
    model = Student
    template_name = 'fee_management/student_fees.html'
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['payments'] = Payment.objects.filter(student=student).order_by('-payment_date')
        context['total_paid'] = Payment.objects.filter(student=student, status='completed').aggregate(total=Sum('amount'))['total'] or 0
        
        # Get all fee structures applicable to the student's course
        student_course = student.course
        context['fee_structures'] = FeeStructure.objects.filter(course=student_course)
        
        # Calculate total fees and outstanding amount
        total_fees = context['fee_structures'].aggregate(total=Sum('amount'))['total'] or 0
        context['total_fees'] = total_fees
        context['outstanding_amount'] = total_fees - context['total_paid']
        
        return context
