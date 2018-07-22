//Deal with multi-step form navigation
var sections = $(".form-section");
var steps = $(".progressbar li");

var sectionHeader = $("#sectionHeader");
const LAST_SECTION = sections.length - 1; 
var currentSection = 0;

navigateTo(currentSection)

function navigateTo(currentSection) {
    currentStepName = steps.eq(currentSection).text()
    sections.eq(currentSection).show();   
    sectionHeader.text(currentStepName)
    //Hides previous button if on first section (currentSection == 0)
    currentSection ? $("#prevBtn").show() : $("#prevBtn").hide();

    if (currentSection == LAST_SECTION) {
        $("#nextBtn").html("Create destination");
    } else {
        $("#nextBtn").html("Next");
    }
};

$(".btn").click(function buttonClick() {
    sections.eq(currentSection).hide()
    if ($(this).attr('id') == "nextBtn") {
        steps.eq(currentSection+1).toggleClass("active");
        currentSection++
    } else {
        steps.eq(currentSection).toggleClass("active");
        currentSection--
    }
    if (currentSection >= LAST_SECTION) {
        $("#submitForm").submit();
        return;
    }
    navigateTo(currentSection)
});

// Creates tags input and the autocomplete
$('#tags').typeahead({
    confirmKeys: [13, 44, 9],
    source: tags
});

/// Initiates map
function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 2,
      center: {lat: 30, lng: 0}
    });
  }

// Changes map viewport and adds pins when country input is changed
$('#country_id').change(function initMap() {
    var address = $('#dest-name').val() + ', ' + $('#country_id').find(":selected").text();
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': address }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 5,
                center: results[0].geometry.location
            });
            var marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location
            });
            $("#lat").val(results[0].geometry.location.lat());
            $("#lng").val(results[0].geometry.location.lng());
        }
    });
});

// Saves image address to server
const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/jacobcwebber/upload/';
const CLOUDINARY_UPLOAD_PRESET = 'pzrian47';

var imgPreview = $('#img-preview');
var fileUpload = $('#file-upload');

fileUpload.on('change', function(event) {
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
        imgPreview.attr('src', res.data.secure_url);
        $('#img-link').attr('value', res.data.secure_url)
    }).catch((e) => {
        console.log(e);
    })
});