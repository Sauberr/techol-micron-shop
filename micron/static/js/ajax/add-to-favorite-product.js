$(document).ready(function() {
    $('.favorite-product-form').on('submit', function(e) {
        e.preventDefault();

        const $form = $(this);
        const $heartIcon = $form.find('.heart-icon');
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
                    $form.hide();
                } else if (response.already_favorited) {
                    showMessage(response.message, response.message_type);
                    $form.hide();
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.message || 'Error adding to favorites';
                showMessage(errorMessage, 'error');
            }
        });
    });
});