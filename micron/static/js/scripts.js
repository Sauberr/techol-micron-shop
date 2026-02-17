(function($) {

    "use strict";

    var searchPopup = function() {
      // Toggle search popup when clicking search button
      $('#header-nav').on('click', '.search-button', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $('.search-popup').toggleClass('is-visible');
      });

      // Close button handler (if exists)
      $('#header-nav').on('click', '.btn-close-search', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $('.search-popup').removeClass('is-visible');
      });

      // Prevent clicks inside the search popup container from closing it
      $(".search-popup-container").on("click", function(e) {
        e.stopPropagation();
      });

      // Close when clicking on the overlay (background), but not on the content
      $(".search-popup").on("click", function(e) {
        if ($(e.target).is(".search-popup")) {
          e.preventDefault();
          $(this).removeClass("is-visible");
        }
      });

      // Close on ESC key
      $(document).keyup(function(e) {
        if (e.which === 27) {
          $(".search-popup").removeClass("is-visible");
        }
      });
    }

    var initProductQty = function(){

      $('.product-qty').each(function(){

        var $el_product = $(this);
        var quantity = 0;

        $el_product.find('.quantity-right-plus').click(function(e){
            e.preventDefault();
            var quantity = parseInt($el_product.find('#quantity').val());
            $el_product.find('#quantity').val(quantity + 1);
        });

        $el_product.find('.quantity-left-minus').click(function(e){
            e.preventDefault();
            var quantity = parseInt($el_product.find('#quantity').val());
            if(quantity>0){
              $el_product.find('#quantity').val(quantity - 1);
            }
        });

      });

    }

    $(document).ready(function() {

      searchPopup();
      initProductQty();

      var swiper = new Swiper(".main-swiper", {
        speed: 500,
        navigation: {
          nextEl: ".swiper-arrow-prev",
          prevEl: ".swiper-arrow-next",
        },
      });

      var swiper = new Swiper(".product-swiper", {
        slidesPerView: 4,
        spaceBetween: 10,
        pagination: {
          el: "#mobile-products .swiper-pagination",
          clickable: true,
        },
        breakpoints: {
          0: {
            slidesPerView: 2,
            spaceBetween: 20,
          },
          980: {
            slidesPerView: 4,
            spaceBetween: 20,
          }
        },
      });

      var swiper = new Swiper(".product-watch-swiper", {
        slidesPerView: 4,
        spaceBetween: 10,
        pagination: {
          el: "#smart-watches .swiper-pagination",
          clickable: true,
        },
        breakpoints: {
          0: {
            slidesPerView: 2,
            spaceBetween: 20,
          },
          980: {
            slidesPerView: 4,
            spaceBetween: 20,
          }
        },
      });

      var swiper = new Swiper(".testimonial-swiper", {
        loop: true,
        navigation: {
          nextEl: ".swiper-arrow-prev",
          prevEl: ".swiper-arrow-next",
        },
      });

    });

})(jQuery);