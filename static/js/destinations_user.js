// Add destination to favorites and change star color when star is clicked
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
            id: $(this).attr('id'),
            action: action
        }
    }).done(function() {
        $(this).toggleClass('star-full');
    }).fail(function(error) {
        console.log(error);
    });
});

// Remove destination to favorites and change star color back to white
// $('.fa-star').click(function(event) {
//     event.preventDefault();
//     $.ajax({
//         type: 'POST',
//         url: '/remove-favorite',
//         context: this,
//         data :{ 
//             id: $(this).attr('id')
//         }
//     }).done(function() {
//         $(this).css({"color": "white"}).removeClass('fa-star').addClass('fa-star-o');
//     }).fail(function(error) {
//         console.log(error);
//     });
// });

// This is not currently working --> need to add deleting favorite when clicking yellow star
// $('.fa-star').click(function() {
//     $(this).css({"color": "white"}).removeClass('fa-star').addClass('fa-star-o');
//     return false;
// });

// $(".fa").click(function(event){
//     event.preventDefault();
//     $(this).toggleClass("favorite");
// });

// Changes color when checkmark is clicked
$('.fa-check').click(function(event) {
    event.preventDefault();
    $(this).toggleClass('explored-full');
})