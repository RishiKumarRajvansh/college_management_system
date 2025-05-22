from django.contrib import admin
from .models import Book, BookIssue

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'isbn', 'availability')
    list_filter = ('availability',)
    search_fields = ('title', 'author', 'isbn')
    list_editable = ('availability',)

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'student', 'book', 'issue_date', 'return_date', 'is_returned', 'fine_amount')
    list_filter = ('is_returned', 'issue_date')
    search_fields = ('student__name', 'book__title')
    date_hierarchy = 'issue_date'
