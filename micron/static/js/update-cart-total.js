function updateCartTotals(response) {
    // Update subtotal
    $('#cart-subtotal').text('$' + response.subtotal);

    // Update bonus points
    $('#cart-bonus-points').text(response.total_bonus_points);

    // Update discount if coupon applied
    if (response.discount) {
        $('#discount-amount').text('– $' + response.discount);
    }

    // Update total after discount
    if (response.total_after_discount) {
        $('#cart-total').text('$' + response.total_after_discount);
    }
}
