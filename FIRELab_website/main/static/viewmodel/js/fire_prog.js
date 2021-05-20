function openCloseToolkit() {
	var toolkit = document.getElementById("toolkit");
	var icon = document.getElementById("close");
	var cp = document.getElementById("cp");

	if (toolkit.style.display == "none") {
		icon.className = "fas fa-times";
		toolkit.style.display = "block";
	}
	else {
		toolkit.style.display = "none";
		icon.className = "fas fa-angle-down";
		cp.title = "Open Toolkit";

	}
}

function openUpload() {
	var upload = document.getElementById("upload");
	var img_prog = document.getElementById("img_prog");
	if ( window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
        img_prog.style.display = 'none';
    } else {
        upload.style.display = 'none';
        img_prog.style.display = 'block';
    }
	
}

function openMap() {
	var map = document.getElementById("map");
	var animationButtons = document.getElementById("animationButtons");
	if ( window.getComputedStyle(map, null).getPropertyValue("display") === 'none' && window.getComputedStyle(animationButtons, null).getPropertyValue("display") === 'none') {
        map.style.display = 'block';
        animationButtons.style.display = 'block';
    } else {
        map.style.display = 'none';
        animationButtons.style.display = 'none';
    }

}

console.log('YEEEET');

    let popUp = $('#popUpGEO');
    let input = $('#coordinates');
    let workingImage = $('#workingImage');
    let pixels = []
    let geocoords = []
    let marker = $('#marker');
    var span_frameid = document.getElementById( 'span_frameid' ).textContent;
    let k = 0;

    popUp.dialog({
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
        console.log("ARRAY PIXELS COORDS", pixels)

        // Move circle here.
        marker.css('top', event.pageY - 50);
        marker.css('left', event.pageX - 25);
        if (marker.css('display') == 'none') {
            marker.css('display', 'block');
        }


        var pos = {my: "left top", at: "left bottom", of: event}
        // console.log("POS: ", pos)
        input.val('')
        popUp.dialog("option", "position", pos)
			.dialog("open");

    });

    $('#submit').click(function () {
        console.log(k++);
        coords = input.val()
        // console.log(coords)
        var coords = input.val().split(",")
        // console.log(coords)
        geocoords.push([parseFloat(coords[0].trim()), parseFloat(coords[1].trim())]);
        console.log("ARRAY GEO COORDS", geocoords);
        marker.css('display', 'none')
        popUp.dialog("close");

    });

    function markerOn() {
        $("#id_marker").attr('checked', true);
        $("#id_eraser").attr('checked', false);
        $("#marker").css("color", "#B55B29")
        $("#eraser").css("color", "")
    }


    // function markerOff() {
    //    $("#id_marker").attr('checked', false);
    //    $("#id_eraser").attr('checked', true);
    //    $("#marker").css("color", "")
    //    $("#eraser").css("color", "#B55B29")
    // }


    function saveCoords() {
        $("#id_frame_id").val(JSON.parse(span_frameid));
        clicking = false;
        $('#id_pixels').val(JSON.stringify(pixels));
        $('#id_geo').val(JSON.stringify(geocoords));
        document.getElementById("georreferencingForm").submit();
    }



	// ANIMAÇÃO QUE TÁ GG PARA OS PROFS MAS É UMA BECS RÚSTICA KSKSKS
	// IT AIN'T MUCH BUT IT'S HONEST WORK <3


	// SHOW THE MAP
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
    var assetLayerGroup = new L.LayerGroup();

    var coords1 =  '[ [40.640957, -8.658695], [40.648772, -8.623848], [40.614901, -8.656635], [40.640957, -8.658695] ]' ;
    var a = JSON.parse(coords1); // string to json
    var polygon1 = L.polygon(a, {color: 'red'}).bindPopup("Coordinates: " + coords1);

    var coords2 =  '[ [40.640957, -8.658695], [40.646764, -8.621168], [40.630807, -8.623571], [40.614133, -8.648682], [40.640957, -8.658695] ]' ;
    var b = JSON.parse(coords2); // string to json
    var polygon2 = L.polygon(b, {color: 'blue'}).bindPopup("Coordinates: " + coords2);


    function displayPolygons(){

        if(!assetLayerGroup.hasLayer(polygon1) || !assetLayerGroup.hasLayer(polygon2)) {
            assetLayerGroup.addLayer(polygon1);
            assetLayerGroup.addTo(mymap);

            setTimeout(function(){
                assetLayerGroup.addLayer(polygon2);
            }, 2000)
            mymap.fitBounds(polygon1.getBounds()).fitBounds(polygon2.getBounds());
        }
        else {
            assetLayerGroup.clearLayers()
            window.clearTimeout()
        }

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


    var popup = L.popup();
    mymap.on('click', function(e){
        popup
            .setLatLng(e.latlng)
            .setContent("You clicked the map at " + e.latlng.toString())
            .openOn(mymap);
    });