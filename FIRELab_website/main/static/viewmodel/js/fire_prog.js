        
        var span_frameid = document.getElementById( 'span_frameid' ).textContent;
        var pixels = [];
        var geoRefPolys=[];
        var geocoords = [];
        var clicking;
        var k =0;
        var currPixelPoint;
        var CoordPopUp = $('#popUpGEO');
        var inputForCoords = $('#coordinates');
        var inputForLocName = $('#coordLocName');
        let workingImage = $('#workingImage');
        var loadPointPopUpDialog = $('#loadPointPopUp');
        var pointNameToSearch = $('#coordNameToSearch');
        var marker = $('#marker');
        var ptNames=[];
        CoordPopUp.dialog({
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


        loadPointPopUpDialog.dialog({
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

        $('#showImage').click(function () {
            workingImage.toggle();
        });

        $('#cp').click(function () {
            $('#toolkit').toggle();
        });

      

        workingImage.mousedown(function (event) {
            if(clicking){
                let x = event.pageX - this.offsetLeft;
                let y = event.pageY - this.offsetTop;
                currPixelPoint=[x, y];
                 // Move circle here.
                marker.css('top', event.pageY - 50);
                marker.css('left', event.pageX - 25);
                var pos = {my: "left top", at: "left bottom", of: event};
                inputForCoords.val('');
                inputForLocName.val('');
                CoordPopUp.dialog("option", "position", pos)
                    .dialog("open");
            }

        });
    

        function saveCoords() {
            $("#id_frame_id").val(JSON.parse(span_frameid));
            clicking = false;
            $('#id_pixels').val(JSON.stringify(pixels));
            $('#ptNames').val(JSON.stringify(ptNames));
            $('#id_geo').val(JSON.stringify(geocoords));
            document.getElementById("georreferencingForm").submit();
        };
         
        $('#loadPoint').click(function () {
            pointNameToSearch.val('');
            loadPointPopUpDialog.dialog("open");
        });


        $('#SearchPointBtn').click(function () {
            var imagePointsAsString = document.getElementById('frame_points').textContent;
            var imagePointsArray =imagePointsAsString.split(";"); //each element of the array is like : "a,POINT (2 7),POINT (0 0)"
            for(let i=0; i<imagePointsArray.length;i++){
                let namePixGeo = imagePointsArray[i].split(',');  //split to access name, pix, geo
                if(namePixGeo[0]==pointNameToSearch.val() && !ptNames.includes(namePixGeo[0])){
                    let pixAux=namePixGeo[1].split(' ');
                    pixels.push([parseFloat(pixAux[0]),parseFloat(pixAux[1])]);
                    let geoAux=namePixGeo[2].split(' ');
                    geocoords.push([parseFloat(geoAux[0]),parseFloat(geoAux[1])]);
                    ptNames.push(namePixGeo[0]);
                    var tr = "<tr>";
                    tr += "<td>"+namePixGeo[0]+"</td>"+"<td>"+pixAux+"</td>"+"<td>"+geoAux+"</td>"+"</tr>";
                    document.getElementById("pixel_table_coords").innerHTML += tr;  
                }
            }
            loadPointPopUpDialog.dialog("close");
        });
       


        $('#undo').click(function () {
           if(pixels.length>0){
                pixels.pop();
                let pix_table =document.getElementById("pixel_table_coords").children;
                pix_table[pix_table.length-1].remove(pix_table[pix_table.length-1].children);
            }
            if(geocoords.length>0){
                geocoords.pop();
            }
            if(ptNames.length>0){
                ptNames.pop();
            }
            if(pixels.length==0){
                $("#pixel_table_coords").attr('hidden', true);
            }
            
        });
        
        

        $('#submit').click(function () {
            $("#pixel_table_coords").attr('hidden', false);
            ptNames.push(inputForLocName.val());
            coords = inputForCoords.val();
            pixels.push(currPixelPoint);
            var pointName = inputForLocName.val();
            var coords = inputForCoords.val().split(",");
            geocoords.push([parseFloat(coords[0].trim()), parseFloat(coords[1].trim())]);
            table_pixel_coord=pixels[pixels.length-1];
            table_geo_coord=geocoords[geocoords.length-1];
            var tr = "<tr>";
            tr += "<td>"+pointName+"</td>"+"<td>"+table_pixel_coord+"</td>"+"<td>"+table_geo_coord+"</td>"+"</tr>";
            document.getElementById("pixel_table_coords").innerHTML += tr;
            CoordPopUp.dialog("close");
        });
      

    

        function markerOn() {
            if($("#id_marker").attr('checked')=='checked'){
                clicking=false;
                $("#id_marker").attr('checked', false);
                $("#id_eraser").attr('checked', true);
                document.getElementById("marker").style.color="";
                $("#eraser").css("color", "#B55B29");
            }
            else{
                clicking=true;
                $("#id_marker").attr('checked', true);
                $("#id_eraser").attr('checked', false);
                document.getElementById("marker").style.color="#B55B29";
                $("#eraser").css("color", "");
            }
            
        };


        $('#zoomIn').click(function () {
            let img = document.getElementById("workingImage");
            let currWidth = img.clientWidth;
            img.style.width = (currWidth+100)+"px";
        })
        
        $('#zoomOut').click(function () {
            let img = document.getElementById("workingImage");
            let currWidth = img.clientWidth;
            img.style.width = (currWidth-100)+"px";

        })

          


        // $('#submit_pol').click(function () {
        //     $("#id_image_id").val("{{frame.id}}");
        //     document.getElementById("UploadCoordFile").submit();
        // });




function openMap() {
	var map = document.getElementById("map");
	var animationButtons = document.getElementById("animationButtons");
	var img_prog = document.getElementById("img_prog");
    img_prog.style.display="none";
	if ( window.getComputedStyle(map, null).getPropertyValue("display") === 'none' && window.getComputedStyle(animationButtons, null).getPropertyValue("display") === 'none') {
        $("#play_tk").css("color", "#B55B29");
	    map.style.display = 'block';
        animationButtons.style.display = 'block';
        workingImage.hide();
    } else {
	    $("#play_tk").css("color", "");
        map.style.display = 'none';
        animationButtons.style.display = 'none';
        workingImage.show();
    }

}
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


function openUpload() {
	var upload = document.getElementById("upload"); 
    var workingImage = document.getElementById("workingImage");
	if ( window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
        workingImage.style.display = 'none';
    } else {
        upload.style.display = 'none';
        workingImage.style.display = 'flex';
    }
	
}
