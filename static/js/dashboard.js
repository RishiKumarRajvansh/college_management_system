// dashboard.js - Dynamic dashboard charts using Chart.js
document.addEventListener('DOMContentLoaded', function() {
    // Store chart instances for later reference
    const chartInstances = {};
    
    // Cache configuration
    const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes
    const CACHE_PREFIX = 'college_mgmt_';
    
    // Cache management functions
    function getCachedData(key) {
        try {
            const cacheKey = `${CACHE_PREFIX}${key}`;
            const cachedItem = localStorage.getItem(cacheKey);
            
            if (!cachedItem) return null;
            
            const { data, timestamp } = JSON.parse(cachedItem);
            const now = new Date().getTime();
            
            // Check if cache is expired
            if (now - timestamp > CACHE_EXPIRY) {
                localStorage.removeItem(cacheKey);
                return null;
            }
            
            return data;
        } catch (e) {
            console.error('Error retrieving cached data:', e);
            return null;
        }
    }
    
    function setCachedData(key, data) {
        try {
            const cacheKey = `${CACHE_PREFIX}${key}`;
            const cacheItem = {
                data: data,
                timestamp: new Date().getTime()
            };
            
            localStorage.setItem(cacheKey, JSON.stringify(cacheItem));
        } catch (e) {
            console.error('Error caching data:', e);
        }
    }
    
    // Function to create a chart
    function createChart(canvasId, type, labels, datasets, options = {}) {
        // Destroy existing chart if it exists
        if (chartInstances[canvasId]) {
            chartInstances[canvasId].destroy();
        }
        
        const ctx = document.getElementById(canvasId).getContext('2d');
        chartInstances[canvasId] = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: datasets
            },
            options: options
        });
        
        return chartInstances[canvasId];
    }
    
    // Add event listeners to refresh buttons
    document.querySelectorAll('.refresh-chart').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.dataset.chart;
            const icon = this.querySelector('i');
            
            // Add spinning animation
            icon.classList.add('fa-spin');
            
            // Force refresh (bypass cache)
            loadChartData(chartId, true).then(() => {
                // Remove spinning after 1 second
                setTimeout(() => {
                    icon.classList.remove('fa-spin');
                }, 1000);
            });
        });
    });
    
    // Function to load chart data
    function loadChartData(chartId, forceRefresh = false) {
        switch(chartId) {
            case 'attendanceChartCanvas':
                return loadAttendanceChart(forceRefresh);
            case 'examPerformanceCanvas':
                return loadExamPerformanceChart(forceRefresh);
            case 'enrollmentChartCanvas':
                return loadEnrollmentChart(forceRefresh);
            case 'feeCollectionCanvas':
                return loadFeeCollectionChart(forceRefresh);
            default:
                return Promise.resolve();
        }
    }    // Load attendance chart function
    function loadAttendanceChart(forceRefresh = false) {
        if (!document.getElementById('attendanceChartCanvas')) {
            return Promise.resolve();
        }
        
        // Try to get data from cache if not forcing refresh
        const cacheKey = 'attendance_stats';
        const cachedData = !forceRefresh ? getCachedData(cacheKey) : null;
        
        if (cachedData) {
            // Use cached data
            createChart(
                'attendanceChartCanvas',
                'doughnut',
                ['Present', 'Absent', 'Late', 'Excused'],
                [{
                    data: [
                        cachedData.present_count,
                        cachedData.absent_count,
                        cachedData.late_count,
                        cachedData.excused_count
                    ],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 205, 86, 0.7)',
                        'rgba(54, 162, 235, 0.7)'
                    ],
                    borderColor: [
                        'rgb(75, 192, 192)',
                        'rgb(255, 99, 132)',
                        'rgb(255, 205, 86)',
                        'rgb(54, 162, 235)'
                    ],
                    borderWidth: 1
                }],
                {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Student Attendance Distribution'
                        }
                    },
                    maintainAspectRatio: false
                }
            );
            
            return Promise.resolve();
        }
        
        // Fetch fresh data
        return fetch('/api/dashboard/attendance-stats/')
            .then(response => response.json())
            .then(data => {
                // Cache the API response
                setCachedData(cacheKey, data);
                
                createChart(
                    'attendanceChartCanvas',
                    'doughnut',
                    ['Present', 'Absent', 'Late', 'Excused'],
                    [{
                        data: [
                            data.present_count,
                            data.absent_count,
                            data.late_count,
                            data.excused_count
                        ],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(255, 205, 86, 0.7)',
                            'rgba(54, 162, 235, 0.7)'
                        ],
                        borderColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 99, 132)',
                            'rgb(255, 205, 86)',
                            'rgb(54, 162, 235)'
                        ],
                        borderWidth: 1
                    }],
                    {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Student Attendance Distribution'
                            }
                        },
                        maintainAspectRatio: false
                    }
                );
            });
    }
    
    // Initialize attendance chart
    if (document.getElementById('attendanceChartCanvas')) {
        loadAttendanceChart();
    }    // Load examination performance chart function
    function loadExamPerformanceChart(forceRefresh = false) {
        if (!document.getElementById('examPerformanceCanvas')) {
            return Promise.resolve();
        }
        
        // Check cache
        const cachedData = !forceRefresh && getCachedData('exam_performance');
        if (cachedData) {
            // Use cached data
            createChart(
                'examPerformanceCanvas',
                'bar',
                cachedData.courses,
                [{
                    label: 'Average Score (%)',
                    data: cachedData.average_scores,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgb(54, 162, 235)',
                    borderWidth: 1
                },
                {
                    label: 'Pass Rate (%)',
                    data: cachedData.pass_rates,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1
                }],
                {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Examination Performance by Course'
                        }
                    }
                }
            );
            
            return Promise.resolve();
        }
        
        return fetch('/api/dashboard/exam-performance/')
            .then(response => response.json())
            .then(data => {
                // Cache the data
                setCachedData('exam_performance', data);
                
                createChart(
                    'examPerformanceCanvas',
                    'bar',
                    data.courses,
                    [{
                        label: 'Average Score (%)',
                        data: data.average_scores,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    },
                    {
                        label: 'Pass Rate (%)',
                        data: data.pass_rates,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 1
                    }],
                    {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Examination Performance by Course'
                            }
                        }
                    }
                );
            });
    }
    
    // Initialize exam performance chart
    if (document.getElementById('examPerformanceCanvas')) {
        loadExamPerformanceChart();
    }    // Load student enrollment chart function
    function loadEnrollmentChart(forceRefresh = false) {
        if (!document.getElementById('enrollmentChartCanvas')) {
            return Promise.resolve();
        }
        
        // Check cache
        const cachedData = !forceRefresh && getCachedData('enrollment_stats');
        if (cachedData) {
            // Use cached data
            createChart(
                'enrollmentChartCanvas',
                'line',
                cachedData.months,
                [{
                    label: 'New Enrollments',
                    data: cachedData.enrollment_counts,
                    backgroundColor: 'rgba(153, 102, 255, 0.3)',
                    borderColor: 'rgb(153, 102, 255)',
                    borderWidth: 2,
                    tension: 0.2,
                    fill: true
                }],
                {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Student Enrollment Trend'
                        }
                    }
                }
            );
            
            return Promise.resolve();
        }
        
        return fetch('/api/dashboard/enrollment-stats/')
            .then(response => response.json())
            .then(data => {
                // Cache the data
                setCachedData('enrollment_stats', data);
                
                createChart(
                    'enrollmentChartCanvas',
                    'line',
                    data.months,
                    [{
                        label: 'New Enrollments',
                        data: data.enrollment_counts,
                        backgroundColor: 'rgba(153, 102, 255, 0.3)',
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 2,
                        tension: 0.2,
                        fill: true
                    }],
                    {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Student Enrollment Trend'
                            }
                        }
                    }
                );
            });
    }
    
    // Initialize enrollment chart
    if (document.getElementById('enrollmentChartCanvas')) {
        loadEnrollmentChart();
    }    // Load fee collection chart function
    function loadFeeCollectionChart(forceRefresh = false) {
        if (!document.getElementById('feeCollectionCanvas')) {
            return Promise.resolve();
        }
        
        // Check cache
        const cachedData = !forceRefresh && getCachedData('fee_collection_stats');
        if (cachedData) {
            // Use cached data
            createChart(
                'feeCollectionCanvas',
                'bar',
                cachedData.months,
                [{
                    label: 'Amount Collected',
                    data: cachedData.amounts,
                    backgroundColor: 'rgba(255, 159, 64, 0.7)',
                    borderColor: 'rgb(255, 159, 64)',
                    borderWidth: 1
                }],
                {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Monthly Fee Collection'
                        }
                    }
                }
            );
            
            return Promise.resolve();
        }
        
        return fetch('/api/dashboard/fee-collection-stats/')
            .then(response => response.json())
            .then(data => {
                // Cache the data
                setCachedData('fee_collection_stats', data);
                
                createChart(
                    'feeCollectionCanvas',
                    'bar',
                    data.months,
                    [{
                        label: 'Amount Collected',
                        data: data.amounts,
                        backgroundColor: 'rgba(255, 159, 64, 0.7)',
                        borderColor: 'rgb(255, 159, 64)',
                        borderWidth: 1
                    }],
                    {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value;
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Monthly Fee Collection'
                            }
                        }
                    }
                );
            });
    }
    
    // Initialize fee collection chart
    if (document.getElementById('feeCollectionCanvas')) {
        loadFeeCollectionChart();
    }
    
    // Auto-refresh charts every 5 minutes
    const autoRefreshInterval = 5 * 60 * 1000; // 5 minutes
    setInterval(() => {
        if (document.getElementById('attendanceChartCanvas')) loadAttendanceChart();
        if (document.getElementById('examPerformanceCanvas')) loadExamPerformanceChart();
        if (document.getElementById('enrollmentChartCanvas')) loadEnrollmentChart();
        if (document.getElementById('feeCollectionCanvas')) loadFeeCollectionChart();
    }, autoRefreshInterval);
});
