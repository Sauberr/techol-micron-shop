function formatPrice(usdAmount) {
    var section = document.querySelector('[data-language]');
    var language = section ? section.dataset.language : (window.CURRENCY_LANGUAGE || 'en');
    var rate = section ? parseFloat(section.dataset.uahRate) || null : (window.CURRENCY_UAH_RATE || null);
    var amount = parseFloat(usdAmount);
    if (isNaN(amount)) return usdAmount;
    if (language === 'uk' && rate) {
        var uah = Math.round(amount * rate);
        return '₴' + uah.toLocaleString('uk-UA');
    }
    return '$' + amount.toFixed(2);
}

