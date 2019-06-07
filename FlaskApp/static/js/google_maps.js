var coordinates;
function showPosition(position) {
    coordinates = new google.maps.LatLng(position.coords.latitude,  position.coords.longitude);
    console.log(position.coords.latitude + " " +position.coords.longitude);
}
let options = {
  enableHighAccuracy: true,
  timeout: 5000,
  maximumAge: 0
};

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition,function (failure) {
            console.log("Couldn't get your location" + failure);
        }, options);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}




function initMap(coordinates) {
    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: {lat: 49.827846, lng: 24.033270}
    });
    directionsDisplay.setMap(map);

    var onChangeHandler = function() {
        calculateAndDisplayRoute(directionsService, directionsDisplay, map);
    };
    document.getElementById('end').addEventListener('change', onChangeHandler);
}
function getHospitalLocation() {
    return {1:new google.maps.LatLng(49.843695, 24.010522),
        2:new google.maps.LatLng(49.841436, 24.018034),
    3:new google.maps.LatLng(49.836523, 24.047091),
    4:new google.maps.LatLng(49.839622, 24.042882)}[document.getElementById('end').value];
}

function calculateAndDisplayRoute(directionsService, directionsDisplay, map) {
    getLocation();
    var marker = new google.maps.Marker({
        'position': coordinates,
        'map': map,
    });
    let dest_val = getHospitalLocation();
    directionsService.route({
        origin: marker.getPosition(),
        destination: dest_val,
        travelMode: 'DRIVING'
    }, function(response, status) {
        if (status === 'OK') {
            directionsDisplay.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

window.onload = function () {
    getLocation();
   initMap(coordinates);
};
