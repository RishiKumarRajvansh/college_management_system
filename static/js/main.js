// Custom JavaScript for College Management System

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Confirmation dialog for delete actions
    $('.btn-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Enable DataTable if present
    if ($.fn.DataTable && $('.datatable').length > 0) {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
            }
        });
    }
    
    // Course selection in bulk attendance form
    $('#id_course').on('change', function() {
        $('#bulk-attendance-form').submit();
    });
    
    // Examination selection in bulk result form
    $('#id_examination').on('change', function() {
        $('#bulk-result-form').submit();
    });
    
    // Date range picker if present
    if ($.fn.daterangepicker && $('.date-range').length > 0) {
        $('.date-range').daterangepicker({
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            alwaysShowCalendars: true,
            locale: {
                format: 'YYYY-MM-DD'
            }
        });
    }
    
    // Calculate total for fee payment
    $('#fee_payment_form .fee-structure').on('change', function() {
        var selectedOption = $(this).find(':selected');
        if (selectedOption.data('amount')) {
            $('#id_amount').val(selectedOption.data('amount'));
        }
    });
    
    // Dependent dropdown for courses and students
    $('#id_course').on('change', function() {
        var courseId = $(this).val();
        if (courseId) {
            $.ajax({
                url: "/student-by-course/",
                data: { 'course_id': courseId },
                success: function(data) {
                    $('#id_student').html(data);
                }
            });
        } else {
            $('#id_student').html('<option value="" selected>---------</option>');
        }
    });
    
    // Print function for reports
    $('.btn-print').on('click', function() {
        window.print();
        return false;
    });
    
    // Toggle password visibility
    $('.toggle-password').on('click', function() {
        var input = $($(this).attr('toggle'));
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            $(this).html('<i class="fa fa-eye-slash"></i>');
        } else {
            input.attr('type', 'password');
            $(this).html('<i class="fa fa-eye"></i>');
        }
    });
    
    // Activate current nav item
    var path = window.location.pathname;
    $('.navbar-nav li a').each(function() {
        var href = $(this).attr('href');
        if (path === href) {
            $(this).addClass('active');
            $(this).closest('.nav-item.dropdown').find('.nav-link.dropdown-toggle').addClass('active');
        }
    });
});

// Function to calculate fine for library book returns
function calculateFine() {
    const returnDate = new Date(document.getElementById('id_return_date').value);
    const actualReturnDate = new Date(document.getElementById('id_actual_return_date').value);
    const finePerDay = 1.00; // $1 per day
    
    if (returnDate && actualReturnDate && actualReturnDate > returnDate) {
        const diffTime = Math.abs(actualReturnDate - returnDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const fine = diffDays * finePerDay;
        document.getElementById('id_fine_amount').value = fine.toFixed(2);
    } else {
        document.getElementById('id_fine_amount').value = '0.00';
    }
}

// Function to generate receipt number for payments
function generateReceiptNumber() {
    const prefix = 'RCT-';
    const randomPart = Math.random().toString(36).substring(2, 8).toUpperCase();
    const timestamp = new Date().getTime().toString().slice(-6);
    document.getElementById('id_receipt_number').value = prefix + randomPart + timestamp;
}
