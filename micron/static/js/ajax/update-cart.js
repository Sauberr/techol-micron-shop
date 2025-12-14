$(document).ready(function() {
    console.log('update-cart.js loaded');
    console.log('Forms found:', $('.update-cart-form').length);
    console.log('Selects found:', $('.update-cart-form select').length);

    // Listen for quantity select change using event delegation
    $(document).on('change', '.update-cart-form select', function() {
        console.log('Select changed!');

        const $select = $(this);
        const $form = $select.closest('form');
        const formData = new FormData($form[0]);
        const csrftoken = getCookie('csrftoken');

        console.log('Form action:', $form.attr('action'));
        console.log('CSRF token:', csrftoken);

        // Show loading state
        $select.css('opacity', '0.5');

        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                console.log('Response:', response);
                if (response.success) {
                    showMessage(response.message, response.message_type);
                    updateCartCounter(response.cart_total);
                    updateCartTotals(response);
                }
            },
            error: function(xhr) {
                console.log('Error:', xhr);
                const errorMessage = xhr.responseJSON?.message || 'Error updating cart';
                showMessage(errorMessage, 'error');
            },
            complete: function() {
                $select.css('opacity', '1');
            }
        });
    });
});
