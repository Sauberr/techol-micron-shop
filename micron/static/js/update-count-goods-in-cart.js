function updateCartCounter(newCount) {
    const cartBadge = document.querySelector('.badge.bg-dark.text-white');
    if (cartBadge) {
        cartBadge.textContent = newCount > 0 ? newCount : '0';
    }
}