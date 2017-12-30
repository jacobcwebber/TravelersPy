// Add/removes destination to favorites and changes star color when star is clicked
$('.fav-star').click(function(event) {
    event.preventDefault();
    if ($(this).hasClass('star-full')) {
        action = "remove";
    } else {
        action = "add";
    }
    $.ajax({
        type: 'POST',
        url: '/alter-favorite',
        context: this,
        data :{ 
            id : $(this).attr('id'),
            action : action
        }
    }).done(function() {
        $(this).toggleClass('star-full');
    }).fail(function(error) {
        console.log(error);
    });
});

// Add/removes destination to explored and change check color when check is clicked
$('.exp-check').click(function(event) {
    event.preventDefault();
    if ($(this).hasClass('exp-full')) {
        action = "remove";
    } else {
        action = "add";
    }
    $.ajax({
        type: 'POST',
        url: '/alter-explored',
        context: this,
        data :{ 
            id : $(this).attr('id'),
            action : action
        }
    }).done(function() {
        $(this).toggleClass('exp-full');
    }).fail(function(error) {
        console.log(error);
    });
});
