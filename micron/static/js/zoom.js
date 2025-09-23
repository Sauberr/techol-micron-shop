(function ($) {
    function initZoom() {
        $('.product-image-container').trigger('zoom.destroy');
        $('.product-image-container').zoom({
            url: $('.main-image').attr('data-zoom-image'),
            touch: false,
        });
    }

    window.changeMainImage = function (thumbnail) {
        const mainImage = document.querySelector('.main-image');
        const newImageUrl = thumbnail.getAttribute('data-full-image');

        mainImage.style.opacity = '0';

        setTimeout(() => {
            mainImage.src = newImageUrl;
            mainImage.setAttribute('data-zoom-image', newImageUrl);
            mainImage.style.opacity = '1';
            initZoom();
        }, 300);

        document.querySelectorAll('.thumbnail-image').forEach(img => {
            img.classList.remove('active');
        });
        thumbnail.classList.add('active');
    };

    $(document).ready(function () {
        initZoom();
    });
})(jQuery);