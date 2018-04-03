//Initializing variables
let firstBox = $('.box:first-of-type')
let featDestWrapper = $('.feat-dest-wrapper');
let featDestImg = $('#feat-dest-img');
let featDestName = $('#feat-dest-name');
let featDestDesc = $('#feat-dest-desc');
let featDestTags = $('feat-dest-tags');

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
        featDestDesc.html(response[0].Description);
        firstBox.removeClass('hidden');
        $.smoothScroll();
        //featDestTags.attr('src', response[0].ImgUrl)
    }).fail((error) => {
        console.log(error);
    });
});