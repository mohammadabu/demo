$('#screen-slide').owlCarousel({
    smartSpeed: 1000,
    margin: 0,
    autoplay: true,
    autoplayHoverPause: true,
    nav: true,
    navText: [
        '<img src="images/prev.png" />',
        '<img src="images/next.png" />'
    ],
    dots: false,
    loop: true,
    margin: 30,
    responsive: {
        0: {
            items: 1
        },
        576: {
            items: 1
        },
        768: {
            items: 1
        },
        1000: {
            items: 1
        }
    }
});


$('#product-slide').owlCarousel({
    loop: true,
    margin: 20,
    nav: false,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 2
        },
        1000: {
            items: 4
        }
    }
})