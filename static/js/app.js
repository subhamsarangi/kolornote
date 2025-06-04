$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Add loading state to forms
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Loading...');
    });
    
    // Confirm navigation away from forms with data
    $('form input, form textarea, form select').on('change input', function() {
        window.onbeforeunload = function() {
            return 'You have unsaved changes. Are you sure you want to leave?';
        };
    });
    
    $('form').on('submit', function() {
        window.onbeforeunload = null;
    });
});