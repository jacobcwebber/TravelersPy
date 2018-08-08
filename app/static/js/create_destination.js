//Variables
var nextBtn = $('#nextBtn');
var prevBtn = $('#prevBtn');
var submitBtn = $('#submitBtn')

var destNameField = $('#destName');
var countryField = $('#country');

var sections = $(".form-section");
var steps = $(".progressbar li");

var sectionHeader = $("#sectionHeader");

const LAST_SECTION = sections.length - 1; 
var currentSection = 0;

//Tab navigation
navigateTo(currentSection)

function navigateTo(currentSection) {
    sections.eq(currentSection).show();   

    //Changes text of section header
    currentStepName = steps.eq(currentSection).text()
    sectionHeader.text(currentStepName)

    //Changes Next button text on pages
    if (currentStepName == 'Location') {
        nextBtn.text("Confirm location")
    } else {
        nextBtn.text("Continue");
    }

    //Makes the metro nav circle large for active step
    //steps.eq(currentSection).

    //Hides previous button if on first section (currentSection == 0)
    currentSection ? $("#prevBtn").show() : $("#prevBtn").hide();

    //Swaps Next button with Submit button if on last section
    if (currentSection == LAST_SECTION) {
        $("#nextBtn").hide();
        $("#submitBtn").show();
    } else {
        $("#nextBtn").show();
        $("#submitBtn").hide();       
    }
};

//JS validation for forms
// $('.form-control').change(() => validateFields(currentSection));

// function validateFields(currentSection) {
//     switch (currentSection) {
//         case 0:
//             if (destNameField.val() != '' && countryField.val() != 0) {
//                 nextBtn.prop('disabled', false);
//             } else {
//                 nextBtn.prop('disabled', true);
//             };
//             break
//         case 1:
            
//     }

// };

//Deals with clicking into metro nav to hop between steps
//TODO: FUNC GOES HERE

$(".btn").click(function() {
    sections.eq(currentSection).hide()
    steps.eq(currentSection).toggleClass("active");
    let btnId = $(this).attr('id')
    if (btnId == "nextBtn") {
        steps.eq(currentSection+1).toggleClass("complete");
        currentSection++
    } else if (btnId == "prevBtn") {
        steps.eq(currentSection).toggleClass("complete");
        currentSection--
    }
    steps.eq(currentSection).toggleClass("active")
    navigateTo(currentSection)
});

$(document).ready(function() {
    $('#country').select2();

    // Creates tags autocomplete
    $('#tags').typeahead({
        hint: true,
        highlight: true,
        accent: true,
        source: tags
    });
});


/// Initiates map
function initMap() {
    var map = new google.maps.Map(document.getElementById('createDestMap'), {
      zoom: 2,
      center: {lat: 0, lng: 0}
    });
  }

// Changes map viewport and adds pin to verify correct location
nextBtn.click(function initMap() {
    var destName = $('#destName').val();
    var countryName =  $('#country').find(':selected').text() != 'Country' ? $('#country').find(':selected').text() : null;

    if (destName || countryName ) {
        let address = destName + ', ' + countryName;
        let geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'address': address }, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
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
            }
        });
    }
    else {
        new google.maps.Map(document.getElementById('createDestMap'), {
            zoom: 1,
            center: new google.maps.LatLng(0, 0)
        });
    }
});

// Saves image address to server
const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/jacobcwebber/upload/';
const CLOUDINARY_UPLOAD_PRESET = 'pzrian47';

var imgPreview = $('#img-preview');
var fileUpload = $('#imgUpload');

fileUpload.on('change', function(event) {
    nextBtn.prop('disabled', true);
    nextBtn.html('<i class="fas fa-spinner fa-spin"></i>');
    var file = event.target.files[0];
    var formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);

    axios({
        url: CLOUDINARY_URL,
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data: formData
    }).then((res) => {
        nextBtn.prop('disabled', false);
        nextBtn.html('Next');
        imgPreview.attr('src', res.data.secure_url);
        $('#imgLink').attr('value', res.data.secure_url)
    }).catch((e) => {
        console.log(e);
    })
});