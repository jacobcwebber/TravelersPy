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