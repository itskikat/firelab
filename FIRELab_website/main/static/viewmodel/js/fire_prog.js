/* VARIABLES */
let toolkit = document.getElementById("toolkit");
let icon = document.getElementById("close");
let cp = document.getElementById("cp");

let img_prog = document.getElementById("img_prog");
let upload = document.getElementById("upload");

let map = document.getElementById("map");
let animationButtons = document.getElementById("animationButtons");
let span_projectid = document.getElementById('span_projectid').textContent.trim();
let span_frameid = document.getElementById('span_frameid').textContent.trim();
let wkts_fromdjango;
let wkts = [];



/* FUNCTIONS */

// Open and Close the Toolkit
function openCloseToolkit() {
	if (toolkit.style.display === "none") {
		icon.className = "fas fa-times";
		toolkit.style.display = "block";
	}
	else {
		toolkit.style.display = "none";
		icon.className = "fas fa-angle-down";
		cp.title = "Open Toolkit";
	}
}

// Show the Image
function imageOn() {
    var workingImage = document.getElementById('workingImage');
    console.log(workingImage)
    if (window.getComputedStyle(workingImage, null).getPropertyValue("display") === 'none') {
        workingImage.style.display = 'block';
        $("#image_tk").css("color", "#B55B29");
    }
    else {
        workingImage.style.display = 'none';
        $("#image_tk").css("color", "");
    }
}

// Open Upload Form (for user input of polygon-coordinates file)
function openUpload() {
	if (window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
        img_prog.style.display = 'none';
    } else {
        upload.style.display = 'none';
        img_prog.style.display = 'block';
    }
}

// BUÉ RÚSTICO MAS TÁ A DAR SORRY
$(document).ready(function() {
    // Ave maria deus abençoe que se o Zagalo vê isto tem um AVC
    if(window.location.href.indexOf("animation") > -1) {
        openMap();
    }
})

// Open and Show the Map, where the animation plays
function openMap() {
    wkts_fromdjango = JSON.parse(document.getElementById('WKTS_HIDDEN').textContent);
    Object.entries(wkts_fromdjango).forEach((entry) => {
        var size = Object.keys.length;
        const [key, value] = entry; // STRING, STRING
        for (var n=0; n<size; n++) {
            var wkt = new Wkt.Wkt();
            wkt.read(value);
            var feature = { "type": "Feature", 'properties': {}, "geometry": wkt.toJson() };
            var geojson_item = L.geoJSON(feature, {color: pickAColor()});
            wkts[parseInt(key)] = geojson_item;
        }
    });
	if ( window.getComputedStyle(map, null).getPropertyValue("display") === 'none'
        && window.getComputedStyle(animationButtons, null).getPropertyValue("display") === 'none')
	{
        $("#play_tk").css("color", "#b55b29");
        document.getElementById( "play_tk" ).setAttribute( "onClick", "javascript: openMap();" );
	    map.style.display = 'block';
        animationButtons.style.display = 'block';
        img_prog.style.display = 'none';
    } else {
	    var url = 'javascript: window.location.replace(\'/projects/'+span_projectid+'/progression?animation);'
	    document.getElementById( "play_tk" ).setAttribute( "onClick", url);
	    closeMap();
	    window.location.replace('/projects/'+span_projectid+'/progression?id='+span_frameid);
    }
}
function closeMap() {
    $("#play_tk").css("color", "");
    map.style.display = 'none';
    animationButtons.style.display = 'none';
    img_prog.style.display = 'flex';
}
function pickAColor() {
    let available_colors = ['blue', 'cadetblue', 'coral', 'cyan', 'grey', 'green', 'orange', 'khaki', 'magenta', 'pink', 'violet', 'gold', 'maroon', 'olive', 'yellow'];
    var random_color = available_colors[Math.floor(Math.random() * available_colors.length)];
    return random_color;
}

// Display that the geo-marker is on
function markerOn() {
    $("#id_marker").attr('checked', true);
    $("#id_eraser").attr('checked', false);
    $("#marker").css("color", "#B55B29")
    $("#eraser").css("color", "")
}

/* ANYGAYS, MORE VARIABLES */

let coordsPopUp = $('#popUpGEO');
let input = $('#coordinates');
let workingImage = $('#workingImage');
let pixels = []
let geocoords = []
let georef_marker = $('#georef_marker');
let k = 0;
let clicking;


// User input for Geographic Coordinates
coordsPopUp.dialog({
    autoOpen: false,
    show: {
        effect: "blind",
        duration: 300
    },
    draggable: true,
    hide: "blind",
    resizable: false,
    height: "auto",
    width: 300,
    modal: true,
});

workingImage.mousedown(function (event) {
    clicking = true
    let x = event.pageX - this.offsetLeft;
    let y = event.pageY - this.offsetTop;
    pixels.push([x, y])
    // Move position marker here.
    georef_marker.css('top', event.pageY - 50);
    georef_marker.css('left', event.pageX - 25);
    if (georef_marker.css('display') === 'none') {
        georef_marker.css('display', 'block');
    }
    var pos = {my: "left top", at: "left bottom", of: event}
    input.val('')
    coordsPopUp.dialog("option", "position", pos)
        .dialog("open");
});

// Place coordinates (Pixels + Geo) in array
$('#submit_geo').click(function () {
    var coords = input.val().split(",")
    geocoords.push([parseFloat(coords[0].trim()), parseFloat(coords[1].trim())]);
    georef_marker.css('display', 'none')
    coordsPopUp.dialog("close");
});

// Submit Polygon File
$('#submit_pol').click(function () {
    $("#id_image_id").val("{{frame.id}}");
    document.getElementById("UploadCoordFile").submit();
});

// POST form with Coordinates (Pixels + Geo)
function saveCoords() {
    $("#id_frame_id").val(JSON.parse(span_frameid));
    clicking = false;
    $('#id_pixels').val(JSON.stringify(pixels));
    $('#id_geo').val(JSON.stringify(geocoords));
    document.getElementById("georreferencingForm").submit();
}



// ANIMAÇÃO QUE TÁ GG PARA OS PROFS MAS É UMA BECS RÚSTICA KSKSKS
// SHOW THE MAP
let mapdiv = document.getElementById('map');
let mymap = L.map(mapdiv).setView([41.179, -8.609], 13); // Porto
let osm = new L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiaXRza2lrYXQiLCJhIjoiY2tubGZyeGR4MGtlNjJxczVkMnc1cGJuMSJ9.AqoknzMtuAATdUKs-gGGTw'
});
osm.addTo(mymap);

let assetLayerGroup = new L.LayerGroup();
// AVE MARIA 2.0
function displayPolygons(){
    var idx = 0;
    wkts.forEach(function (item, indice, array) {
        // ITEM == GEOJSON
        if (!assetLayerGroup.hasLayer(item) && idx === 0) {
            assetLayerGroup.addLayer(item);
            idx+=1;
            assetLayerGroup.addTo(mymap);
            mymap.fitBounds(item.getBounds());
        }
        else if (idx !== 0) {
            setTimeout(function(){
                assetLayerGroup.addLayer(item);
            }, 2000)
            mymap.fitBounds(item.getBounds());
        }
        else {
            assetLayerGroup.clearLayers()
            window.clearTimeout()
        }
    });
}
let count;
function start() {
    count = setInterval(displayPolygons, 4000)
}
function stop() {
    clearInterval(count)
}
$("#drawPolygonButton").on('click', (start));
$("#stopDraw").on('click', (stop))

// Clicking the map at X displays the coordinates
var popup = L.popup();
mymap.on('click', function(e){
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + e.latlng.toString())
        .openOn(mymap);
});