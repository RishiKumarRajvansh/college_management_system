from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Book, BookIssue
from .forms import BookForm, BookIssueForm
from datetime import date
from decimal import Decimal


class LibraryDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view for Library Management module"""
    template_name = 'library_management/dashboard.html'
    model = Book
    context_object_name = 'recent_books'
    
    def get_queryset(self):
        return Book.objects.order_by('-created_at')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        context['available_books'] = Book.objects.filter(availability=True).count()
        context['issued_books'] = Book.objects.filter(availability=False).count()
        context['recent_issues'] = BookIssue.objects.filter(is_returned=False).order_by('-issue_date')[:5]
        return context


# Book Views
class BookListView(LoginRequiredMixin, ListView):
    """View for listing all books"""
    model = Book
    template_name = 'library_management/book_list.html'
    context_object_name = 'books'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Book.objects.all().order_by('title')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
            
        # Apply availability filter if provided
        availability = self.request.GET.get('availability')
        if availability:
            if availability == 'available':
                queryset = queryset.filter(availability=True)
            elif availability == 'issued':
                queryset = queryset.filter(availability=False)
            
        return queryset


class BookCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new book"""
    model = Book
    form_class = BookForm
    template_name = 'library_management/book_form.html'
    success_url = reverse_lazy('book_list')
    success_message = "Book '%(title)s' was created successfully"


class BookDetailView(LoginRequiredMixin, DetailView):
    """View for showing book details"""
    model = Book
    template_name = 'library_management/book_detail.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['issue_history'] = BookIssue.objects.filter(book=book).order_by('-issue_date')
        return context


class BookUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an existing book"""
    model = Book
    form_class = BookForm
    template_name = 'library_management/book_form.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'
    success_message = "Book '%(title)s' was updated successfully"
    
    def get_success_url(self):
        return reverse('book_detail', kwargs={'book_id': self.object.book_id})


class BookDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a book"""
    model = Book
    template_name = 'library_management/book_confirm_delete.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'
    success_url = reverse_lazy('book_list')
    
    def delete(self, request, *args, **kwargs):
        book = self.get_object()
        messages.success(request, f"Book '{book.title}' was deleted successfully")
        return super().delete(request, *args, **kwargs)


# Book Issue Views
class BookIssueListView(LoginRequiredMixin, ListView):
    """View for listing all book issues"""
    model = BookIssue
    template_name = 'library_management/book_issue_list.html'
    context_object_name = 'issues'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BookIssue.objects.all().order_by('-issue_date')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(book__title__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__registration_number__icontains=search_query)
            )
            
        # Apply status filter if provided
        status = self.request.GET.get('status')
        if status:
            if status == 'returned':
                queryset = queryset.filter(is_returned=True)
            elif status == 'not_returned':
                queryset = queryset.filter(is_returned=False)
            
        return queryset


class BookIssueCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new book issue"""
    model = BookIssue
    form_class = BookIssueForm
    template_name = 'library_management/book_issue_form.html'
    success_url = reverse_lazy('book_issue_list')
    success_message = "Book issued successfully"
    
    def form_valid(self, form):
        # Update book availability to False (not available)
        book = form.cleaned_data['book']
        book.availability = False
        book.save()
        return super().form_valid(form)


class BookIssueDetailView(LoginRequiredMixin, DetailView):
    """View for showing book issue details"""
    model = BookIssue
    template_name = 'library_management/book_issue_detail.html'
    context_object_name = 'issue'
    pk_url_kwarg = 'issue_id'


class BookIssueUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an existing book issue"""
    model = BookIssue
    form_class = BookIssueForm
    template_name = 'library_management/book_issue_form.html'
    context_object_name = 'issue'
    pk_url_kwarg = 'issue_id'
    success_message = "Book issue was updated successfully"
    
    def get_success_url(self):
        return reverse('book_issue_detail', kwargs={'issue_id': self.object.issue_id})


class BookReturnView(LoginRequiredMixin, UpdateView):
    """View for returning a book"""
    model = BookIssue
    template_name = 'library_management/book_return_form.html'
    fields = ['actual_return_date', 'fine_amount']
    context_object_name = 'issue'
    pk_url_kwarg = 'issue_id'
    success_url = reverse_lazy('book_issue_list')
    
    def get_initial(self):
        # Set default values for the form
        initial = super().get_initial()
        initial['actual_return_date'] = date.today()
        
        # Calculate fine if returned after due date
        issue = self.get_object()
        if date.today() > issue.return_date and not issue.is_returned:
            # Calculate days late
            days_late = (date.today() - issue.return_date).days
            # Assuming fine rate of $1 per day
            fine_amount = Decimal(days_late * 1.0)
            initial['fine_amount'] = fine_amount
        return initial
    
    def form_valid(self, form):
        # Update book availability to True (available)
        issue = self.get_object()
        issue.is_returned = True
        issue.book.availability = True
        issue.book.save()
        
        messages.success(self.request, f"Book '{issue.book.title}' has been returned successfully")
        return super().form_valid(form)


class StudentBooksView(LoginRequiredMixin, ListView):
    """View for showing all books issued to a specific student"""
    model = BookIssue
    template_name = 'library_management/student_books.html'
    context_object_name = 'issues'
    paginate_by = 10
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return BookIssue.objects.filter(student_id=student_id).order_by('-issue_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')
        from student_management.models import Student
        student = get_object_or_404(Student, pk=student_id)
        context['student'] = student
        context['current_books'] = BookIssue.objects.filter(student=student, is_returned=False).count()
        context['total_borrowed'] = BookIssue.objects.filter(student=student).count()
        context['total_fine'] = BookIssue.objects.filter(student=student).exclude(fine_amount=0).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0
        return context
