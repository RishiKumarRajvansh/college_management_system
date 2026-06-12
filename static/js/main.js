// Custom JavaScript for College Management System

document.addEventListener('DOMContentLoaded', function() {
    // Lightweight Tailwind-friendly dropdowns, modals and tabs replace the old UI bundle.
    document.querySelectorAll('[data-menu-toggle]').forEach(function(toggle) {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            const menu = document.getElementById(toggle.getAttribute('aria-controls')) || toggle.nextElementSibling;
            if (!menu) {
                return;
            }
            document.querySelectorAll('.dropdown-menu.show').forEach(function(openMenu) {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                }
            });
            menu.classList.toggle('show');
        });
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                menu.classList.remove('show');
            });
        }
    });

    document.querySelectorAll('[data-modal-target]').forEach(function(trigger) {
        trigger.addEventListener('click', function(event) {
            event.preventDefault();
            const modal = document.getElementById(trigger.dataset.modalTarget);
            if (modal) {
                modal.classList.add('show');
                modal.setAttribute('aria-hidden', 'false');
            }
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(function(trigger) {
        trigger.addEventListener('click', function() {
            const modal = trigger.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
                modal.setAttribute('aria-hidden', 'true');
            }
        });
    });

    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.classList.remove('show');
                modal.setAttribute('aria-hidden', 'true');
            }
        });
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(function(modal) {
                modal.classList.remove('show');
                modal.setAttribute('aria-hidden', 'true');
            });
        }
    });

    document.querySelectorAll('[data-tab-target]').forEach(function(tab) {
        tab.addEventListener('click', function() {
            const target = document.querySelector(tab.dataset.tabTarget);
            const tabList = tab.closest('[role="tablist"]');
            const content = target ? target.parentElement : null;

            if (!target || !tabList || !content) {
                return;
            }

            tabList.querySelectorAll('[data-tab-target]').forEach(function(item) {
                item.classList.remove('active');
                item.setAttribute('aria-selected', 'false');
            });
            content.querySelectorAll('.tab-pane').forEach(function(pane) {
                pane.classList.remove('show', 'active');
            });

            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            target.classList.add('show', 'active');
        });
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.style.transition = 'opacity 0.2s ease';
            alert.style.opacity = '0';
            window.setTimeout(function() {
                alert.remove();
            }, 250);
        });
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
