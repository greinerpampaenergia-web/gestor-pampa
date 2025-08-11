document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm task deletion
    const deleteButtons = document.querySelectorAll('.btn-delete-task');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro que desea eliminar esta tarea?')) {
                e.preventDefault();
            }
        });
    });

    // Task toggle confirmation for completed tasks
    const toggleButtons = document.querySelectorAll('.btn-toggle-task');
    toggleButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const taskTitle = button.getAttribute('data-task-title');
            const isCompleted = button.getAttribute('data-completed') === 'true';
            
            let message;
            if (isCompleted) {
                message = `¿Marcar "${taskTitle}" como pendiente?`;
            } else {
                message = `¿Marcar "${taskTitle}" como completada?`;
            }
            
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Real-time filter updates
    const statusFilter = document.getElementById('status-filter');
    const responsibleFilter = document.getElementById('responsible-filter');
    
    if (statusFilter && responsibleFilter) {
        function updateFilters() {
            const status = statusFilter.value;
            const responsible = responsibleFilter.value;
            
            const params = new URLSearchParams();
            if (status !== 'all') params.set('status', status);
            if (responsible) params.set('responsible', responsible);
            
            const newUrl = window.location.pathname + 
                          (params.toString() ? '?' + params.toString() : '');
            window.location.href = newUrl;
        }
        
        statusFilter.addEventListener('change', updateFilters);
        responsibleFilter.addEventListener('change', updateFilters);
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor complete todos los campos obligatorios');
            }
        });
    });

    // Clear filter button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            window.location.href = window.location.pathname;
        });
    }

    // Task counter update
    updateTaskCounters();
});

function updateTaskCounters() {
    const totalTasks = document.querySelectorAll('.task-card').length;
    const completedTasks = document.querySelectorAll('.task-completed').length;
    const pendingTasks = totalTasks - completedTasks;
    const overdueTasks = document.querySelectorAll('.task-overdue').length;
    
    // Update counters in the DOM if elements exist
    const totalCounter = document.getElementById('total-tasks');
    const completedCounter = document.getElementById('completed-tasks');
    const pendingCounter = document.getElementById('pending-tasks');
    const overdueCounter = document.getElementById('overdue-tasks');
    
    if (totalCounter) totalCounter.textContent = totalTasks;
    if (completedCounter) completedCounter.textContent = completedTasks;
    if (pendingCounter) pendingCounter.textContent = pendingTasks;
    if (overdueCounter) overdueCounter.textContent = overdueTasks;
}
