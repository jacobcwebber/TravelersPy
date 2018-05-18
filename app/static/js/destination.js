//Setup for map
function initMap() {
    var latLng = {lat: lat, lng: lng};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: latLng,
        mapTypeId: 'hybrid'
    });

    var marker = new google.maps.Marker({
        position: latLng,
        map: map
    });
};

