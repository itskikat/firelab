$(document).ready(function () {

    // UPLOAD BUTTON
    document.querySelectorAll('#file-upload__button').forEach(function (button) {
        const hiddenInput = button.parentElement.querySelector('.file-upload__input');
        const label = button.parentElement.querySelector('.file-upload__label');
        const defaultLabelText = 'No file selected';

        // Set default text for label
        label.textContent = defaultLabelText;
        label.title = defaultLabelText;
        
        button.addEventListener('click', function(){
            hiddenInput.click();
        });

        hiddenInput.addEventListener('change', function(){
            // console.log(hiddenInput.files);
            const fileName = Array.from(hiddenInput.files).map(function(file) {
                return file.name;
            });
            // console.log(fileName);

            label.textContent = fileName || defaultLabelText;
            label.title = label.textContent;

        });

    });


    
});

function drawMap() {
    var mapdiv = document.getElementById('map');

    var mymap = L.map(mapdiv).setView([40.6405, -8.6538], 13);

    var osm = new L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: 'pk.eyJ1IjoiaXRza2lrYXQiLCJhIjoiY2tubGZyeGR4MGtlNjJxczVkMnc1cGJuMSJ9.AqoknzMtuAATdUKs-gGGTw'
    });
    osm.addTo(mymap);

    var coords =  '[ [40.640957, -8.658695], [40.648772, -8.623848], [40.614901, -8.656635], [40.640957, -8.658695] ]' ;
        //var coords = document.getElementById("polygon-coord").value;

    var a = JSON.parse(coords); // string to json

    var polygon = L.polygon(a, {color: 'red'});
    polygon.addTo(mymap);
    polygon.bindPopup("Coordinates: " + coords);

    mymap.fitBounds(polygon.getBounds());

    var popup = L.popup();
    mymap.on('click', function(e){
        popup
            .setLatLng(e.latlng)
            .setContent("You clicked the map at " + e.latlng.toString())
            .openOn(mymap);
    });
}
