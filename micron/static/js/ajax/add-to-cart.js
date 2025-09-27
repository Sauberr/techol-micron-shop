$(document).ready(function() {
    const BUTTON_RESET_DELAY = 2000;

    function resetButton($button, originalContent) {
        $button.html(originalContent);
        $button.prop('disabled', false);
    }

    function setButtonSuccess($button) {
        $button.html('<i class="fa-solid fa-check"></i>');
        $button.prop('disabled', true);
    }

    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();

        const $form = $(this);
        const $button = $form.find('.add-to-cart-btn');
        const formData = new FormData(this);
        const csrftoken = getCookie('csrftoken');
        const originalContent = $button.html();

        setButtonSuccess($button);

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

                    setTimeout(() => {
                        resetButton($button, originalContent);
                    }, BUTTON_RESET_DELAY);
                } else {
                    resetButton($button, originalContent);
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error adding product to cart';
                showMessage(errorMessage, 'error');
                resetButton($button, originalContent);
            }
        });
    });
});