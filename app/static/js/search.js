$('#location').typeahead({
  hint: false,
  highlight: true,
  minLength: 2,
  source: locations
});

$('#keywords').typeahead({
  hint: false,
  highlight: true,
  minLength: 2,
  source: tags
})

// Show or hide Placeholder depending on existence of tags
$('#keywords').on('itemAdded', () => {
  $('.search-input input').attr('placeholder', '');
});

$('#keywords').on('itemRemoved', () => {
  if ($('.label').length == 0) {
    $('.search-input input').attr('placeholder', 'Filter by keywords');
  }
});

$(window).on('load', function() {
  $('.spinner').addClass('hide');
  $('.five-wide').removeClass('hide').addClass('fade-in');
});
