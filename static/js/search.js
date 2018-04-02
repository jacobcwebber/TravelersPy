// Typeahead setup for Location input box
$('#location').typeahead({
    hint: false,
    highlight: true,
    minLength: 1,
    source: locationsList
});

//Typeahead with Tagsinput setup for Keywords input box
$('#keywords').tagsinput({
    confirmKeys: [9, 13, 44],
    trimValue: true,
    typeahead: {
        afterSelect: function() {this.$element.val(''); },
        source: tagsList
    },
    freeInput: false    
});

// Show or hide Placeholder depending on existence of tags
$('#keywords').on('itemAdded', function(e) {
    $('.search-input input').attr('placeholder', '')
});

$('#keywords').on('itemRemoved', function(e) {
    if ($('.label').length == 0) {
        $('.search-input input').attr('placeholder', 'Filter by keywords')
    }
});