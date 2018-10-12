//Variables
var allBtns = $('.btn')
var nextBtn = $('#nextBtn');
var prevBtn = $('#prevBtn');
var submitBtn = $('#submitBtn')

var destNameField = $('#destName');
var countryField = $('#country');
var destinationField = $('.cke_editable p');

var sections = $(".form-section");
var steps = $(".progressbar li");
var countryCode;

var sectionHeader = $("#sectionHeader");

const LAST_SECTION = sections.length - 1;
var currentSection = 0;

//Tab navigation
navigateTo(currentSection)

function navigateTo(currentSection) {
    sections.eq(currentSection).show();

    //Changes text of section header
    currentStepName = steps.eq(currentSection).text();
    sectionHeader.text(currentStepName);

    //Changes Next button text on pages
    if (currentStepName == 'Location') {
        nextBtn.text("Confirm location & Continue");
    } else {
        nextBtn.text("Continue");
    }

    //Hides previous button if on first section (currentSection == 0)
    currentSection ? prevBtn.show() : prevBtn.hide();

    //Swaps Next button with Submit button if on last section
    if (currentSection == LAST_SECTION) {
        nextBtn.hide();
        submitBtn.show();
    } else {
        nextBtn.show();
        submitBtn.hide();
    }
};

$('#updateSearchTerm').click(function () {
    sections.eq(2).hide();
    steps.eq(2).removeClass("active");
    steps.eq(0).addClass("active");
    currentSection = 0;
    navigateTo(currentSection);
})

//Deals with clicking into completed steps in metro nav to hop between steps
$(".progressbar").on('click', 'li.complete', function (event) {
    var clickedStepNum = parseInt((event.target.id).slice(-1)) - 1;
    if (clickedStepNum == currentSection) { return }

    sections.eq(currentSection).hide();
    steps.eq(currentSection).removeClass("active");
    steps.eq(clickedStepNum).addClass("active");
    currentSection = clickedStepNum;
    navigateTo(currentSection);
    updateConfirmTab();
})

function updateConfirmTab() {
    $('#destinationConfirm').text(destNameField.val());
    $('#countryConfirm').text(countryField.val());
    $('#descriptionConfirm').text(destinationField.val());
}

allBtns.click(function () {
    sections.eq(currentSection).hide();
    steps.eq(currentSection).removeClass("active");
    let btnId = $(this).attr('id');
    if (btnId == "nextBtn") {
        steps.eq(currentSection + 1).addClass("complete");
        currentSection++;
    } else if (btnId == "prevBtn") {
        currentSection--;
    }
    steps.eq(currentSection).addClass("active");
    navigateTo(currentSection);
});

$(document).ready(function () {
    $('#country').select2();

    // Creates tags autocomplete
    $('#tags').typeahead({
        hint: true,
        highlight: true,
        accent: true,
        source: tags
    });
});

//Tags
var tagsInput = document.querySelector('#tags');
tagify = new Tagify(tagsInput, {
    autocomplete: false,
    enforceWhitelist: true,
    whitelist: tags,
    dropdown: {
        enabled: 1,
        maxItems: 5
    }
});

/// Initiates map
function initMap() {
    new google.maps.Map(document.getElementById('createDestMap'), {
        zoom: 2,
        center: { lat: 0, lng: 0 }
    });
}

//Call to updateMap on Next button click or any navigation using metro nav
nextBtn.on("click", () => {
    updateMap();
    updateConfirmTab();
});

$(".progressbar").on('click', 'li.complete', updateMap);

//Ajax call to get country_code when country is changed
countryField.on("change", function () {
    if ($(this).val() != '0') {
        $.ajax({
            type: 'GET',
            url: '/admin/get-country-code',
            context: this,
            data: {
                id: $(this).val()
            }
        }).done((response) => {
            countryCode = response;
        }).fail((error) => {
            console.log(error);
        })
    }
});

// Changes map viewport and adds pin to verify correct location
function updateMap() {
    var destName = $('#destName').val();
    var countryName = $('#country').find(':selected').text();

    if (destName || countryName) {
        let geocoder = new google.maps.Geocoder();
        geocoder.geocode({
            address: destName,
            componentRestrictions: {
                country: countryCode
            }
        }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                $('.dest-not-found').hide();
                $('#createDestMap').show();
                let map = new google.maps.Map(document.getElementById('createDestMap'), {
                    zoom: 5,
                    center: results[0].geometry.location
                });
                new google.maps.Marker({
                    map: map,
                    position: results[0].geometry.location,
                    title: destName ? destName : countryName
                });
                $("#lat").val(results[0].geometry.location.lat());
                $("#lng").val(results[0].geometry.location.lng());
            } else if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
                $('.dest-not-found').show();
                $('#createDestMap').hide();
                $('#destSearchTerm').text(destName + ', ' + countryName);
            } else {
                console.log('Geocode failed due to:' + status);
            }
        });
    }
    else {
        new google.maps.Map(document.getElementById('createDestMap'), {
            zoom: 2,
            center: new google.maps.LatLng(0, 0)
        });
    };
};

// Saves image address to server
const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/jacobcwebber/image/upload';
const CLOUDINARY_UPLOAD_PRESET = 'pzrian47';
const CLOUDINARY_API_KEY = 144913695731324;


//Stop dropzone from trying to find the element until it's created
Dropzone.autoDiscover = false;

//Configure image dropzone
var dropzone = new Dropzone(document.getElementById("dzUpload"), {
    uploadMultiple: false,
    maxFiles: 1,
    addRemoveLinks: true,
    acceptedFiles: '.jpg,.png,.jpeg,.gif',
    url: CLOUDINARY_URL,
    dictDefaultMessage: "Drop image here or click to upload."
});

dropzone.on('sending', function (file, xhr, formData) {
    formData.append('api_key', CLOUDINARY_API_KEY);
    formData.append('timestamp', Date.now() / 1000 | 0);
    formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET)
});

dropzone.on('success', function (file, response) {
    file.previewElement.classList.add("dz-success");
});