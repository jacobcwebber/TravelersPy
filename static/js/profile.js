var markers = [];
var map;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 25, lng: 0},
        zoom: 2,
        mapTypeId: 'hybrid'
    });

    addMarkers(locations);
}

function addMarkers(locations) {
    for (i=0; i<locations.length; i++) {
        var pos = new google.maps.LatLng(locations[i][0], locations[i][1])
        var marker = new google.maps.Marker({
            position: pos,
            map: map,
            title: locations[i][2]
        });
        markers.push(marker)
    }
}

function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null)
    }
    markers = [];
}

// Shows markers according to tab clicked
$('.pill-element').click(function(event) {
    view = $(this).attr('id');
    $(this).siblings().removeClass('active');
    $(this).addClass('active');
    $.ajax({
        type: 'POST',
        url: '/change-map',
        data: {
            view: view
        }
    }).done(function(response) {
        clearMarkers();
        addMarkers(response);
    }).fail(function(error) {
        console.log(error);
    });
});