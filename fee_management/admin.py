from django.contrib import admin
from .models import FeeCategory, FeeStructure, Payment

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('fee_category_id', 'name', 'description')
    search_fields = ('name',)

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('fee_structure_id', 'category', 'course', 'amount', 'academic_year', 'due_date')
    list_filter = ('category', 'academic_year', 'course')
    search_fields = ('category__name', 'course__course_name')
    date_hierarchy = 'due_date'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'student', 'fee_structure', 'amount', 'payment_date', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('student__name', 'receipt_number', 'transaction_id')
    date_hierarchy = 'payment_date'
    readonly_fields = ('receipt_number',)
