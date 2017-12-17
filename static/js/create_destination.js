$('#next-btn').on("click", function() {
    var geocoder = new google.maps.Geocoder();
    var location = $('#dest-name').val();
    geocoder.geocode( {'address' : location}, function(response, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var lat = response[0].geometry.location.lat();
            var lng = response[0].geometry.location.lng();
            storeLocation(lat, lng)
        }
    })
});

function storeLocation(lat, lng) {
    $.ajax({
        type: 'POST',
        url: '/create-destination',
        data: {
            lat: lat,
            lng: lng
        },
        error: function(e) {
            console.log(e);
        }
    });
}