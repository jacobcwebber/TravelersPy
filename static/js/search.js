// Options used by fuse.js for search
var options = {
    shouldSort: true,
    threshold: 0.20,
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
        'DestName',
        'CountryName',
        'Tags'
    ]
};

var allIds = []

$('.dest').each(function() {
    allIds.push(this.id)
});

// First takes the search query and return JSON of results, then uses the results to filter
var getDests = $.ajax({
    type: 'POST',
    url: '/search-results'
});

// Triggers search on button click
$('.search-btn').click(function(event) {
    searchDests();
});

// Triggers search on enter key press when in input box
$('.search').keypress(function(e) {
    if(e.which == 13) {
        searchDests();
    }
});

function searchDests() {
    var query = $('.search-input').val();
    $('.no-results').addClass('hidden');
    getDests.done(function(dests) {
        var ids = [];
        var fuse = new Fuse(dests, options);
        var results = fuse.search(query);
        console.log(dests);
        for (var i = 0; i < results.length; i++) {
            ids.push("dest".concat(results[i].DestID))
        }
        for (var i = 0; i < allIds.length; i++) {
            $(`.dest#${allIds[i]}`).removeClass('hidden');
            if (ids.indexOf(allIds[i]) == -1 && query != '') {
                $(`.dest#${allIds[i]}`).addClass('hidden');
            }
        }
        if (Object.keys(results).length == 0 && query != '') {
            $('.no-results').removeClass('hidden')
        };
    });    
}


