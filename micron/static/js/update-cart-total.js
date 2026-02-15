function updateCartTotals(response) {
    $('#cart-subtotal').text('$' + response.subtotal);

    $('#cart-bonus-points').text(response.total_bonus_points);

    if (response.discount) {
        $('#discount-amount').text('– $' + response.discount);
        $('#cart-total-row').show();
    }

    if (response.total_after_discount) {
        $('#cart-total').text('$' + response.total_after_discount);
    }
}
