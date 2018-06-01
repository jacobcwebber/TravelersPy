// Initialize tooltips
$(function () {
    $('[rel="tooltip"]').tooltip({
        delay: {'show': 500, 'hide': 100}
    })
})

// Add/removes destination to favorites, changes star color, and pops up notification when star is clicked
$('.fa-star').click(function(event) {
    event.preventDefault();
    if ($(this).hasClass('star-full')) {
        action = "remove";
        $(this).tooltip({title: 'Add to Favorites'});
    } else {
        action = "add";
        $(this).tooltip({title: 'Remove from Favorites'});
    }
    $.ajax({
        type: 'POST',
        url: '/alter-favorite',
        context: this,
        data: { 
            id : $(this).attr('id'),
            action : action
        }
    }).done(() => {
        if ($(this).hasClass('star-full')) {
            $('#toast').attr("text", "Removed from Favorites")
            toast.show();
        } else {
            $('#toast').attr("text", "Added to Favorites")
            toast.show()
        }
        $(this).toggleClass('star-full');
    }).fail((error) => {
        console.log(error);
    });
});

// Add/removes destination to explored, changes check color, and pops up notification when check is clicked
$('.fa-check').click(function(event) {
    event.preventDefault();
    if ($(this).hasClass('exp-full')) {
        action = "remove";
        $(this).tooltip({title: 'Add to Explored'});
    } else {
        action = "add";
        $(this).tooltip({title: 'Remove from Explored'});
    }
    $.ajax({
        type: 'POST',
        url: '/alter-explored',
        context: this,
        data :{ 
            id : $(this).attr('id'),
            action : action
        }
    }).done(() => {
        if ($(this).hasClass('exp-full')) {
            $('#toast').attr("text", "Removed from Explored destinations")
            toast.show();
        } else {
            $('#toast').attr("text", "Added to Explored destinations")
            toast.show()
        }
        $(this).toggleClass('exp-full');
    }).fail((error) => {
        console.log(error);
    });
});
