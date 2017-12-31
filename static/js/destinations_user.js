// Add/removes destination to favorites, changes star color, and pops up notification when star is clicked
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
        if ($(this).hasClass('star-full')) {
            toastUnfav.show();
        } else {
            toastFav.show()
        }
        $(this).toggleClass('star-full');
    }).fail(function(error) {
        console.log(error);
    });
});

// Add/removes destination to explored, changes check color, and pops up notification when check is clicked
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
        if ($(this).hasClass('exp-full')) {
            toastUnexp.show();
        } else {
            toastExp.show()
        }
        $(this).toggleClass('exp-full');
    }).fail(function(error) {
        console.log(error);
    });
});

//Hides background images for 500ms on page load then fades then in over 2s
$(document).ready(function() {
    $(".dest-image").hide();
    setTimeout(function() {
        $(".dest-image").fadeIn(1000);
    }, 500);    
});
