// Add destination to favorites and change star color when star is clicked
$('.fa-star-o').click(function(event) {
    event.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/add-favorite',
        context: this,
        data :{ 
            id: $(this).attr('id')
        }
    }).done(function() {
        $(this).css({"color": "yellow"}).removeClass('fa-star-o').addClass('fa-star');
    }).fail(function(error) {
        console.log(error);
    });
});

// This is not currently working --> need to add deleting favorite when clicking yellow star
$('.fa-star').click(function() {
    $(this).css({"color": "white"}).removeClass('fa-star').addClass('fa-star-o');
    return false;
});