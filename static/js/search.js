//Initializing variables
let featBox = $('.box:first-of-type')
let featDestWrapper = $('.feat-dest-wrapper');
let featDestImg = $('#feat-dest-img');
let featDestName = $('#feat-dest-name');
let featCountryName = $('#feat-country-name');
let featDestDesc = $('#feat-dest-desc');
let featDestTags = $('#feat-dest-tags');

let resultsBox = $('box:last-of-type');

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
    maxTags: 5,
    typeahead: {
        afterSelect: function() {this.$element.val(''); },
        source: tagsList
    },
    freeInput: false    
});

// Show or hide Placeholder depending on existence of tags
$('#keywords').on('itemAdded', () => {
    $('.search-input input').attr('placeholder', '');
});

$('#keywords').on('itemRemoved', () => {
    if ($('.label').length == 0) {
        $('.search-input input').attr('placeholder', 'Filter by keywords');
    }
});

$('.item-mid').click((e) => {
    let id = e.target.id;
    $.ajax({
        type: 'POST',
        url: '/alter-featured-dest',
        data: {
            id: id
        }
    }).done((response) => {
        featDestImg.attr('src', response[0].ImgUrl);
        featDestName.text(response[0].DestName);
        featCountryName.text(response[0].CountryName);
        featDestDesc.html(response[0].Description);
        featDestTags.empty();

        let tags = response[1];
        $.each(tags, (i) => { 
            featDestTags.append(`<a href='/search?keywords=${tags[i].TagName}' class='label label-lg'>${tags[i].TagName} </a>`)
        });
        featBox.removeClass('hide');
        $.smoothScroll({
            offset: -64,
            scrollTarget: featBox
        });
    }).fail((error) => {
        console.log(error);
    });
});
 
$(window).on("load", function() {
    $('.loading').addClass('hide');
    $('.five-wide').removeClass('hide');
});