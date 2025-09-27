function updateCartTotals(response) {
        $('.total-section .d-flex:contains("Subtotal:") span:last-child').text('$' + response.subtotal);

        $('.total-section .me-1').text(response.total_bonus_points);

        if (response.total_after_discount) {
            $('.total-amount').text('$' + response.total_after_discount);
        }
    }