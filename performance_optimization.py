"""
performance_optimization.py - Utility script for optimizing database performance with large datasets

This script provides database optimization techniques for the College Management System
when dealing with large datasets, including:
- Query optimization
- Database index creation
- Batch processing
- Caching configuration
"""

import os
import sys
import django
import time
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.db import connection, transaction, models
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from reporting.models import Report, Notification
from student_management.models import Student
from course_management.models import Course
from attendance_management.models import Attendance
from django.db.models import Count, Q

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('performance_optimization')

def add_database_indexes():
    """
    Create database indexes to speed up common queries.
    Run this function after schema migrations but before adding large amounts of data.
    """
    logger.info("Creating database indexes for performance optimization...")
    
    with connection.cursor() as cursor:
        # Check if index exists before creating
        # Student table indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_name 
            ON student_management_student(name);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_registration 
            ON student_management_student(registration_number);
        """)
        
        # Course table indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_name 
            ON course_management_course(name);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_code 
            ON course_management_course(code);
        """)
        
        # Attendance table indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_date 
            ON attendance_management_attendance(date);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_status 
            ON attendance_management_attendance(status);
        """)
        
        # Notification table indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notification_read 
            ON reporting_notification(read);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notification_user_read 
            ON reporting_notification(user_id, read);
        """)
        
        # Report table indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_report_type_date 
            ON reporting_report(report_type, created_at);
        """)
    
    logger.info("Database indexes created successfully")

def optimize_queries():
    """
    Analyze and optimize slow database queries
    """
    logger.info("Beginning query optimization analysis...")
    
    # Test query performance
    def measure_query_time(query_func, name):
        start = time.time()
        result = query_func()
        duration = time.time() - start
        logger.info(f"Query '{name}' took {duration:.4f} seconds")
        return result, duration
    
    # Original slow query for student attendance
    def slow_student_attendance_query():
        return list(Student.objects.filter(
            attendance__date__gte='2025-01-01'
        ).distinct())
    
    # Optimized query using select_related or prefetch_related
    def optimized_student_attendance_query():
        return list(Student.objects.filter(
            attendance__date__gte='2025-01-01'
        ).prefetch_related('attendance_set').distinct())
    
    # Original slow query for course reports
    def slow_course_report_query():
        courses = Course.objects.all()
        result = []
        for course in courses:
            students = Student.objects.filter(course=course).count()
            result.append({'course': course, 'student_count': students})
        return result
    
    # Optimized query using annotation
    def optimized_course_report_query():
        return list(Course.objects.annotate(
            student_count=Count('student')
        ))
    
    # Compare performance
    _, slow_time1 = measure_query_time(slow_student_attendance_query, "Slow student attendance query")
    _, fast_time1 = measure_query_time(optimized_student_attendance_query, "Optimized student attendance query")
    
    _, slow_time2 = measure_query_time(slow_course_report_query, "Slow course report query")
    _, fast_time2 = measure_query_time(optimized_course_report_query, "Optimized course report query")
    
    # Report improvement
    improvement1 = (slow_time1 - fast_time1) / slow_time1 * 100 if slow_time1 > 0 else 0
    improvement2 = (slow_time2 - fast_time2) / slow_time2 * 100 if slow_time2 > 0 else 0
    
    logger.info(f"Query optimization achieved {improvement1:.1f}% improvement for attendance queries")
    logger.info(f"Query optimization achieved {improvement2:.1f}% improvement for course report queries")
    
    # Return a list of optimization recommendations
    recommendations = []
    
    if improvement1 > 20:
        recommendations.append("Use prefetch_related when loading students with attendance records")
    if improvement2 > 20:
        recommendations.append("Use annotate instead of querying in loops for aggregation")
    
    # Check for unindexed queries
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
        """)
        indices = cursor.fetchall()
        
        # Check if core tables are indexed
        indexed_tables = [idx[0] for idx in indices]
        core_tables = ['student_management_student', 'course_management_course', 'attendance_management_attendance']
        
        for table in core_tables:
            if table not in indexed_tables:
                recommendations.append(f"Create indexes for {table} table")
    
    return recommendations

def implement_batch_processing():
    """
    Implement batch processing for large data operations
    """
    logger.info("Setting up batch processing helpers...")
    
    def batch_create(model_class, object_list, batch_size=1000):
        """
        Create objects in batches to avoid memory issues
        """
        total = len(object_list)
        logger.info(f"Batch creating {total} {model_class.__name__} objects")
        
        for i in range(0, total, batch_size):
            batch = object_list[i:i+batch_size]
            model_class.objects.bulk_create(batch)
            logger.info(f"Created batch {i//batch_size + 1} ({len(batch)} objects)")
    
    def batch_update(queryset, update_dict, batch_size=1000):
        """
        Update objects in batches to avoid memory issues
        """
        total = queryset.count()
        logger.info(f"Batch updating {total} objects")
        
        # Get primary key name
        pk_name = queryset.model._meta.pk.name
        
        # Process in batches
        processed = 0
        while processed < total:
            # Get a batch of IDs
            id_batch = list(queryset.order_by(pk_name).values_list(pk_name, flat=True)[processed:processed+batch_size])
            if not id_batch:
                break
                
            # Update this batch
            queryset.model.objects.filter(**{f"{pk_name}__in": id_batch}).update(**update_dict)
            
            processed += len(id_batch)
            logger.info(f"Updated batch {processed//batch_size} ({len(id_batch)} objects)")
    
    # Example usage functions
    def example_batch_create():
        """Example of batch creation for student records"""
        start = time.time()
        # Create a large list of sample students
        student_objects = []
        for i in range(5000):
            student = Student(
                name=f"Test Student {i}",
                registration_number=f"S{100000+i}",
                email=f"student{i}@example.com",
                date_of_birth="2000-01-01"
            )
            student_objects.append(student)
            
        # Use batch create instead of a loop
        batch_create(Student, student_objects)
        
        duration = time.time() - start
        logger.info(f"Batch creation completed in {duration:.2f} seconds")
    
    def example_batch_update():
        """Example of batch updating for attendance records"""
        # Update all absent records to late in batches
        start = time.time()
        
        attendance_queryset = Attendance.objects.filter(status='absent')
        batch_update(attendance_queryset, {'status': 'late'})
        
        duration = time.time() - start
        logger.info(f"Batch update completed in {duration:.2f} seconds")
    
    # Return the batch processing functions for use in other modules
    return {
        'batch_create': batch_create,
        'batch_update': batch_update,
        'example_batch_create': example_batch_create,
        'example_batch_update': example_batch_update
    }

def setup_caching():
    """
    Configure and test caching mechanisms
    """
    logger.info("Setting up and testing caching configuration...")
    
    # Define test caching function
    def test_caching_performance():
        # Key for this cache test
        cache_key = 'performance_test_all_students'
        
        # Uncached query
        start = time.time()
        students_uncached = list(Student.objects.all()[:1000])
        uncached_time = time.time() - start
        logger.info(f"Uncached query took {uncached_time:.4f} seconds")
        
        # Store in cache
        cache.set(cache_key, students_uncached, 60)
        
        # Cached query
        start = time.time()
        students_cached = cache.get(cache_key)
        cached_time = time.time() - start
        logger.info(f"Cached query took {cached_time:.4f} seconds")
        
        # Calculate improvement
        if uncached_time > 0:
            improvement = (uncached_time - cached_time) / uncached_time * 100
            logger.info(f"Caching improved performance by {improvement:.1f}%")
            return improvement
        return 0
    
    # Example of caching dashboard data
    def cache_dashboard_data():
        # Cache attendance stats
        attendance_data = {
            'present_count': Attendance.objects.filter(status='present').count(),
            'absent_count': Attendance.objects.filter(status='absent').count(),
            'late_count': Attendance.objects.filter(status='late').count(),
            'excused_count': Attendance.objects.filter(status='excused').count()
        }
        cache.set('dashboard_attendance_stats', attendance_data, 5 * 60)  # Cache for 5 minutes
        
        # Cache student enrollment data 
        # Assuming there's a date field for enrollment
        enrollment_data = Student.objects.extra(
            select={'enrollment_date': "date(created_at)"}
        ).values('enrollment_date').annotate(
            count=Count('id')
        ).order_by('enrollment_date')[:10]
        
        cache.set('dashboard_enrollment_stats', list(enrollment_data), 10 * 60)  # Cache for 10 minutes
        
        logger.info("Dashboard data successfully cached")
    
    # Test caching
    improvement = test_caching_performance()
    
    # Cache dashboard data
    cache_dashboard_data()
    
    # Return caching recommendations
    recommendations = []
    
    if improvement < 90:
        recommendations.append("Current cache backend may not be optimal. Consider using Redis or Memcached")
        
    if 'FileBasedCache' in settings.CACHES['default']['BACKEND']:
        recommendations.append("File-based cache is not recommended for production. Switch to Redis or Memcached")
    
    if improvement > 0:
        recommendations.append(f"Caching is working correctly. Query time improved by {improvement:.1f}%")
        
    return recommendations

def cleanup():
    """
    Clean up test data and optimize database
    """
    logger.info("Performing database cleanup and optimization...")
    
    try:
        # Remove any test data if needed
        # Student.objects.filter(name__startswith='Test Student').delete()
        
        # Vacuum database (PostgreSQL only)
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE;")
            
        logger.info("Database cleanup and optimization completed")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def run_all_optimizations():
    """
    Run all optimization functions and return a summary
    """
    logger.info("Starting complete optimization process...")
    
    optimizations = {
        "Database Indexes": add_database_indexes,
        "Query Optimizations": optimize_queries,
        "Batch Processing": implement_batch_processing,
        "Caching Setup": setup_caching
    }
    
    results = {}
    recommendations = []
    
    for name, func in optimizations.items():
        logger.info(f"Running {name}...")
        try:
            result = func()
            results[name] = "Success"
            
            # Collect recommendations if returned
            if isinstance(result, list):
                recommendations.extend(result)
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}")
            results[name] = f"Error: {str(e)}"
    
    # Perform cleanup
    cleanup()
    
    # Return summary
    summary = {
        "results": results,
        "recommendations": recommendations
    }
    
    logger.info(f"Optimization process completed. Found {len(recommendations)} recommendations.")
    return summary

if __name__ == "__main__":
    logger.info("Starting performance optimization script...")
    
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Database performance optimization')
    parser.add_argument('--indexes', action='store_true', help='Create database indexes')
    parser.add_argument('--queries', action='store_true', help='Optimize slow queries')
    parser.add_argument('--batch', action='store_true', help='Set up batch processing')
    parser.add_argument('--cache', action='store_true', help='Configure caching')
    parser.add_argument('--all', action='store_true', help='Run all optimizations')
    
    args = parser.parse_args()
    
    # Run selected optimization or all
    if args.all:
        summary = run_all_optimizations()
        print("\n=== Optimization Summary ===")
        for task, result in summary["results"].items():
            print(f"{task}: {result}")
        
        print("\n=== Recommendations ===")
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"{i}. {rec}")
            
    else:
        if args.indexes:
            add_database_indexes()
        if args.queries:
            recommendations = optimize_queries()
            print("\n=== Query Optimization Recommendations ===")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        if args.batch:
            batch_funcs = implement_batch_processing()
            print("Batch processing helpers ready for import")
        if args.cache:
            recommendations = setup_caching()
            print("\n=== Caching Recommendations ===")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
    
    logger.info("Performance optimization script completed")
