$(document).ready(function() {
    $('.delete-from-cart-form').on('submit', function(e) {
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
                    $form.closest('.cart-item').remove();

                    if (response.cart_total === 0) {
                        $('.cart-items').html('<div class="text-center"><h3 class="mb-4">Your cart is empty</h3><a href="/products/" class="action-btn continue-btn">Start Shopping</a></div>');
                        $('.cart-summary').hide();
                    }
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error removing product from cart';
                showMessage(errorMessage, 'error');
            }
        });
    });
});