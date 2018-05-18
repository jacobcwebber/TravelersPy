//Setup for carousel
window.onload=function(){
    $('.images').slick( {
            fade: true,
            arrows: false,
            autoplay: true,
            autoplaySpeed: 5000
    });
};

//Setup for map
// function initMap() {
//     var geocoder = new google.maps.Geocoder();
//     var destinations = $('#dest-name').text();
//     geocoder.geocode( {'address' : location}, function(response, status) {
//         if (status == google.maps.GeocoderStatus.OK) {
//             var lat = response[0].geometry.location.lat();
//             var lng = response[0].geometry.location.lng();
//         }

//         latLng = {lat: lat, lng: lng};

//         var map = new google.maps.Map(document.getElementById('map'), {
//           zoom: 4,
//           center: latLng
//         });

//         var marker = new google.maps.Marker({
//           position: latLng,
//           map: map
//         });
//     });
// }
