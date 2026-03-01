$(document).ready(function() {
    function resetButton($button, originalContent) {
        $button.html(originalContent);
        $button.prop('disabled', false);
    }

    function setButtonSuccess($button) {
        $button.html('<i class="fa-solid fa-check"></i>');
        $button.prop('disabled', true);
    }

    $(document).on('submit', '#coupon-remove-form', function(e) {
        e.preventDefault();

        const $form = $(this);
        const $button = $form.find('button[type="submit"]');
        const originalContent = $button.html();
        const csrftoken = getCookie('csrftoken');
        const applyUrl = $('.coupon-section').data('apply-url');

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

                    const applyFormHtml = `
                        <form action="${applyUrl}" method="post" class="d-flex gap-2" id="coupon-apply-form">
                            ${$form.find('[name="csrfmiddlewaretoken"]').prop('outerHTML')}
                            <input type="text" name="code" class="form-control" placeholder="Enter coupon code" maxlength="50" required id="id_code">
                            <button class="update-btn" type="submit">Apply Coupon</button>
                        </form>
                    `;

                    $('.coupon-section').html(applyFormHtml);

                    // Обновляем все цены через updateCartTotals — discount=0 гарантирует скрытие Total
                    updateCartTotals(response);
                } else {
                    resetButton($button, originalContent);
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error removing coupon';
                showMessage(errorMessage, 'error');
                resetButton($button, originalContent);
            }
        });
    });
});
