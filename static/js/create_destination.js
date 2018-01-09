var currentTab = 0;
showTab(currentTab);

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

function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 1,
      center: {lat: 0, lng: 0}
    });
  }


$('#countryId').change(function initMap() {
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
        }
    });
});