function updateCartTotals(response) {
    $('#cart-subtotal').text(formatPrice(response.subtotal));
    $('#cart-bonus-points').text(response.total_bonus_points);

    var discount = parseFloat(response.discount);
    if (response.discount !== undefined && !isNaN(discount) && discount > 0) {
        $('#discount-amount').text('– ' + formatPrice(response.discount));
        $('#cart-total').text(formatPrice(response.total_after_discount));
        $('#cart-total-row').show();
    } else {
        $('#cart-total-row').hide();
    }
}
