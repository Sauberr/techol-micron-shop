$(document).ready(function() {
    function resetButton($button, originalContent) {
        $button.html(originalContent);
        $button.prop('disabled', false);
    }

    function setButtonSuccess($button) {
        $button.html('<i class="fa-solid fa-check"></i>');
        $button.prop('disabled', true);
    }

    $(document).on('submit', '#coupon-apply-form', function(e) {
        e.preventDefault();

        const $form = $(this);
        const $button = $form.find('button[type="submit"]');
        const originalContent = $button.html();
        const csrftoken = getCookie('csrftoken');
        const removeUrl = $('.coupon-section').data('remove-url');

        setButtonSuccess($button);

        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    showMessage(response.message, response.message_type);

                    const couponHtml = `
                        <div class="coupon-badge">
                            <span class="coupon-code">${response.coupon.code}</span>
                            <span>(${response.coupon.discount}% off)</span>
                            <div class="discount-amount" id="discount-amount">– ${formatPrice(response.discount_amount)}</div>
                        </div>
                        <form method="POST" action="${removeUrl}" id="coupon-remove-form">
                            ${$form.find('[name="csrfmiddlewaretoken"]').prop('outerHTML')}
                            <button type="submit" class="delete-btn">Remove Coupon</button>
                        </form>
                    `;

                    $('.coupon-section').html(couponHtml);
                    $('#cart-subtotal').text(formatPrice(response.subtotal));
                    $('#cart-total').text(formatPrice(response.total_after_discount));
                    $('#cart-total-row').show();
                } else {
                    showMessage(response.message || 'Invalid coupon code', 'error');
                    resetButton($button, originalContent);
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error applying coupon';
                showMessage(errorMessage, 'error');
                resetButton($button, originalContent);
            }
        });
    });
});
