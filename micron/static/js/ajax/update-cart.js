$(document).ready(function() {
    $('.update-cart-form').on('submit', function(e) {
        e.preventDefault();

        const $form = $(this);
        const formData = new FormData(this);
        const csrftoken = getCookie('csrftoken');

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
                if (response.success) {
                    showMessage(response.message, response.message_type);
                    updateCartCounter(response.cart_total);
                    updateCartTotals(response);
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error updating cart';
                showMessage(errorMessage, 'error');
            }
        });
    });
});