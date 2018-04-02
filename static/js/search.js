
// Options used for search
var options = {
    shouldSort: true,
    threshold: 0.075,
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
        'DestName',
        'CountryName',
        'Tags',
        'ContName'
    ]
};

var allDestIds = [];

// Adds the IDs of all destinations to an array
$('.item').each(function() {
    allDestIds.push(this.id)
});

// Triggers search on button click
$('#adv-search-btn').click(function(event) {
    advSearch()
});

// Triggers search on enter key press when in input box
$('#adv-search').keypress(function(e) {
    if(e.which == 13) {
        advSearch();
    }
});

function advSearch() {
    advSearchQuery = $('#adv-search').val(); 
    $('.item-group').toggleClass('hidden');
    $('#loading').toggleClass('hidden');

    $.getJSON({
        dataType: "json",
        url: "/getSearchResults",
        data: {
            q: advSearchQuery
        }
    }).done(function(response) {
        console.log(response);
        $('#loading').toggleClass('hidden');

    });
}

// $('#adv-search').tagsinput({
//     confirmKeys: [9, 13, 44],
//     trimValue: true,
//     typeahead: {
//         afterSelect: function() {this.$element.val(''); },
//         source: searchList
//     },
//     freeInput: true    
// });

$('#search-filter-btn').click(function() {
    $('#filter-search').toggleClass('hidden');
});


$("#location").typeahead({
    hint: false,
    highlight: true,
    minLength: 1,
    source: locationsList
});