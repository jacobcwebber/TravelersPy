var currentTab = 0;
showTab(currentTab);

$('#tags').val(myTags);

function showTab(n) {
    var x = document.getElementsByClassName("tab");
    x[n].style.display = "block";
    if (n == 0) {
        document.getElementById("prevBtn").style.display = "none";
    } else {
        document.getElementById("prevBtn").style.display = "inline";
    }
    if (n == (x.length - 1)) {
        document.getElementById("nextBtn").innerHTML = "Submit"
    } else {
        document.getElementById("nextBtn").innerHTML = "Next"
    }
}

function nextPrev(n) {
    var x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none";
    currentTab = currentTab + n;
    if (currentTab >= x.length) {
        document.getElementById("submitForm").submit();
        return false;
    }
    showTab(currentTab)
}

// Creates tags input and the autocomplete
$('#tags').tagsinput({
    confirmKeys: [13, 44, 9],
    maxTags: 10,
    trimValue: true,
    typeahead: {
      afterSelect: function(val) {this.$element.val(""); },
      showHintOnFocus: true,
      source: allTags
    },
    freeInput: false
});

function initMap() {
    var address = $('#dest-name').val() + ', ' + $('#countryId').find(":selected").text();
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
    }
)};


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
    }).then(function(res) {
        imgPreview.attr('src', res.data.secure_url);
        $('#img-link').attr('value', res.data.secure_url)
    }).catch(function(error) {
        console.log(error);
    })
});