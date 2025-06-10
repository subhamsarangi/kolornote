$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
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