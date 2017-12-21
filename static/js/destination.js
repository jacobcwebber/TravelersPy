//Setup for carousel
window.onload=function(){
    $('.images').slick( {
        fade: true,
        arrows: false,
        autoplay: true,
        autoplaySpeed: 5000,
        touchMove: true
    });
};

function initMap() {
    var geocoder = new google.maps.Geocoder();
    var location = $('#dest-name').text();
    geocoder.geocode( {'address' : location}, function(response, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var lat = response[0].geometry.location.lat();
            var lng = response[0].geometry.location.lng();
        }

        latLng = {lat: lat, lng: lng};

        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 5,
          center: latLng
        });

        var marker = new google.maps.Marker({
          position: latLng,
          map: map
        });
    });
}
