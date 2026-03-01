$(document).ready(function() {
    const minRange = document.getElementById('min_range');
    const maxRange = document.getElementById('max_range');
    const minLabel = document.getElementById('min_price_label');
    const maxLabel = document.getElementById('max_price_label');
    const resetBtn = document.getElementById('reset-filter-btn');
    const discountSelect = document.getElementById('discount');
    const categorySelect = document.getElementById('category');
    const orderSelect = document.getElementById('order');
    const productGrid = document.getElementById('product-grid');

    if (!minRange || !maxRange || !minLabel || !maxLabel || !resetBtn || !discountSelect || !categorySelect || !orderSelect || !productGrid) {
        console.error('Required filter elements not found');
        return;
    }

    const initialMinPrice = parseFloat(minRange.dataset.minPrice) || 0;
    const initialMaxPrice = parseFloat(minRange.dataset.maxPrice) || 1000;
    const globalMinPrice = initialMinPrice;
    const globalMaxPrice = initialMaxPrice;

    let filterTimeout = null;

    function initializeSliders(min = globalMinPrice, max = globalMaxPrice, value_min = null, value_max = null) {
        minRange.min = min;
        minRange.max = max;
        maxRange.min = min;
        maxRange.max = max;

        minRange.value = value_min !== null ? value_min : min;
        maxRange.value = value_max !== null ? value_max : max;

        updatePriceLabels();
    }

    function updatePriceLabels() {
        const minValue = parseFloat(minRange.value);
        const maxValue = parseFloat(maxRange.value);

        minLabel.textContent = minValue.toFixed(2);
        maxLabel.textContent = maxValue.toFixed(2);

        const percent1 = ((minValue - minRange.min) / (minRange.max - minRange.min)) * 100;
        const percent2 = ((maxValue - minRange.min) / (minRange.max - minRange.min)) * 100;

        $('.range-track').css('background',
            `linear-gradient(to right,
            #ddd ${percent1}%,
            #212529 ${percent1}%,
            #212529 ${percent2}%,
            #ddd ${percent2}%)`
        );
    }

    function filterProducts(page = 1) {
        const minPrice = parseFloat(minRange.value);
        const maxPrice = parseFloat(maxRange.value);
        const discount = discountSelect.value;
        const category = categorySelect.value;
        const order = orderSelect.value;

        const params = new URLSearchParams();
        params.append('min_price', minPrice);
        params.append('max_price', maxPrice);
        params.append('page', page);

        if (discount) {
            params.append('discount', discount);
        }
        if (category) {
            params.append('category', category);
        }
        if (order) {
            params.append('order', order);
        }

        // Keep search query from URL if it exists
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search_query');
        if (searchQuery) {
            params.append('search_query', searchQuery);
        }


        productGrid.style.opacity = '0.5';

        // Get the current language prefix from URL
        const pathParts = window.location.pathname.split('/');
        const langPrefix = pathParts[1] ? '/' + pathParts[1] : '';
        const productsUrl = langPrefix + '/products/';

        $.ajax({
            type: 'GET',
            url: productsUrl,
            data: params.toString(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    productGrid.innerHTML = response.html;
                    productGrid.style.opacity = '1';

                    bindPaginationEvents();
                    bindFavoriteEvents();

                    const newUrl = window.location.pathname + '?' + params.toString();
                    window.history.pushState({}, '', newUrl);
                } else {
                    console.error('Filter error:', response.error);
                    productGrid.style.opacity = '1';
                    alert('Error filtering products: ' + (response.error || 'Unknown error'));
                }
            },
            error: function(xhr) {
                console.error('Error filtering products:', xhr);
                console.error('Response:', xhr.responseText);
                productGrid.style.opacity = '1';

                let errorMsg = 'Error filtering products';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg += ': ' + xhr.responseJSON.error;
                }
                alert(errorMsg);
            }
        });
    }

    function filterWithDebounce(page = 1) {
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(function() {
            filterProducts(page);
        }, 300);
    }

    function bindPaginationEvents() {
        $('.pagination a.page-link').off('click').on('click', function(e) {
            e.preventDefault();
            const page = $(this).data('page');
            if (page) {
                filterProducts(page);
                $('html, body').animate({
                    scrollTop: $('#product-grid').offset().top - 100
                }, 300);
            }
        });
    }

    function bindFavoriteEvents() {
        $('.favorite-product-form').off('submit').on('submit', function(e) {
            e.preventDefault();

            const $form = $(this);
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
                    if (response.success || response.already_favorited) {
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
    }

    // Live filtering on slider input
    minRange.addEventListener('input', function() {
        const minValue = parseFloat(this.value);
        const maxValue = parseFloat(maxRange.value);

        if (minValue > maxValue) {
            this.value = maxValue;
        }
        updatePriceLabels();
        filterWithDebounce(1);
    });

    maxRange.addEventListener('input', function() {
        const maxValue = parseFloat(this.value);
        const minValue = parseFloat(minRange.value);

        if (maxValue < minValue) {
            this.value = minValue;
        }
        updatePriceLabels();
        filterWithDebounce(1);
    });

    // Reset button
    resetBtn.addEventListener('click', function(e) {
        e.preventDefault();
        initializeSliders();
        discountSelect.value = '';
        categorySelect.value = '';
        orderSelect.value = 'price';
        filterProducts(1);

        const newUrl = window.location.pathname;
        window.history.pushState({}, '', newUrl);
    });

    discountSelect.addEventListener('change', function() {
        filterProducts(1);
    });

    categorySelect.addEventListener('change', function() {
        filterProducts(1);
    });

    orderSelect.addEventListener('change', function() {
        filterProducts(1);
    });

    const urlParams = new URLSearchParams(window.location.search);
    const selectedMinPrice = parseFloat(urlParams.get('min_price')) || initialMinPrice;
    const selectedMaxPrice = parseFloat(urlParams.get('max_price')) || initialMaxPrice;
    const selectedDiscount = urlParams.get('discount') || '';
    const selectedCategory = urlParams.get('category') || '';
    const selectedOrder = urlParams.get('order') || 'price';

    initializeSliders(globalMinPrice, globalMaxPrice, selectedMinPrice, selectedMaxPrice);
    discountSelect.value = selectedDiscount;
    categorySelect.value = selectedCategory;
    orderSelect.value = selectedOrder;

    bindPaginationEvents();
    bindFavoriteEvents();
});

