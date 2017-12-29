$(".dest").hover(function() {
    $("dest-box-header").css("visibility", "visible");
})

$('.fa-star-o').click(function() {
    $.ajax({
        type: 'POST',
        url: '/add-favorite',
        data : {
            id: $(this).attr('id')
        },
        success: function() {
            $(this).css({"color": "yellow"}).removeClass('fa-star-o').addClass('fa-star');
            console.log('Great success!')
            return false
        },
        error: function(error) {
            console.log(error);
            return false;
        }
    });
});

$('.fa-star').click(function() {
    $(this).css({"color": "white"}).removeClass('fa-star').addClass('fa-star-o');
    return false;
});