
        let map = document.getElementById("map");
        let animationButtons = document.getElementById("animationButtons");
        let span_projectid = document.getElementById('span_projectid').textContent.trim();
        let span_frameid = document.getElementById('span_frameid').textContent.trim();
        var img_prog = document.getElementById("img_prog");
        let wkts_fromdjango;
        let wkts = [];
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
        var loadImagePopUpDialog = $('#loadImagePopUp');
        var pointNameToSearch = $('#coordNameToSearch');
        var imageNameToSearch = $('#imageNameToSearch');
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
        loadImagePopUpDialog.dialog({
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

        function openCloseToolkit() {
            var toolkit = document.getElementById("toolkit");
            var icon = document.getElementById("close");
            var cp = document.getElementById("cp");

            if (toolkit.style.display == "none") {
                icon.className = "fas fa-times";
                toolkit.style.display = "block";
                cp.title = "Close Toolkit";
            }
            else {
                toolkit.style.display = "none";
                icon.className = "fas fa-angle-down";
                cp.title = "Open Toolkit";

            }
        }


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

        $('#loadImage').click(function () {
            imageNameToSearch.val('');
            loadImagePopUpDialog.dialog("open");
        });
       

        $('#SearchPointBtn').click(function () {
            var imagePointsAsString = document.getElementById('frame_points').textContent;
            console.log(imagePointsAsString);
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
            if(ptNames.length>0){
                $("#pixel_table_coords").attr('hidden', false);
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
        
        function isFloat(n){
            return Number(n) === n && n % 1 !== 0;
        }
        function isInt(n){
            return Number(n) === n && n % 1 === 0;
        }
        

        $('#submit_geo').click(function () {
            $('#previouslySavedPoints').val($('#default').val())

            console.log("reset")
            $("#pixel_table_coords").attr('hidden', false);
            var coords = inputForCoords.val().split(",");
            if((isFloat(parseFloat(coords[0].trim())) && isFloat(parseFloat(coords[1].trim())) || (isInt(parseFloat(coords[0].trim())) && isInt(parseFloat(coords[1].trim()))))){
                if(parseFloat(coords[0].trim())<=90 && (parseFloat(coords[1].trim())>=-90) && parseFloat(coords[1].trim())<=180 && (parseFloat(coords[1].trim())>=-180)){
                    console.log(parseFloat(coords[0].trim()));
                    ptNames.push(inputForLocName.val());
                    pixels.push(currPixelPoint);
                    var pointName = inputForLocName.val();
                    geocoords.push([parseFloat(coords[0].trim()), parseFloat(coords[1].trim())]);
                    table_pixel_coord=pixels[pixels.length-1];
                    table_geo_coord=geocoords[geocoords.length-1];
                    var tr = "<tr>";
                    tr += "<td>"+pointName+"</td>"+"<td>"+table_pixel_coord+"</td>"+"<td>"+table_geo_coord+"</td>"+"</tr>";
                    document.getElementById("pixel_table_coords").innerHTML += tr;
                }
                else{
                    alert("Wrong input");
                    $("#pixel_table_coords").attr('hidden', true);
                }
            }
            else{
                alert("Wrong input");
                $("#pixel_table_coords").attr('hidden', true);
            }
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


//TUTORIAL

const tutorial = document.getElementById("tutorial");
const tips = document.getElementById("tips");
const goback = document.getElementById("goBack");

var step = 1;
var className;

function openTutorial() {
    
   goback.style.color = "transparent";
    
   tutorial.style.display = "flex";
  
}

function closeTutorial() {
   tutorial.style.display = "none";
   step = 1;
   tips.innerHTML = "Click <i class='fa fa-folder-open fa-lg' ></i> and input the name of the image to work on";
  
}

function next() {
  goback.style.color = "#E4C3B1";
    step++;
    if (step === 1) {
      goback.style.color = "transparent";
      tips.innerHTML = "Click <i class='fa fa-image fa-lg'></i> to open an available image";

    }
    else if (step === 2) {
   
        tips.innerHTML = "Click <i class='fa fa-map-marker-alt fa-lg' ></i> to input the geographic coordinates";
      
    }
    else if (step === 3) {
      
        tips.innerHTML = "Click <i class='fa fa-undo fa-lg'></i> if you want to delete the last coordinate inputed";

    }
    else if (step === 4) {
    
        tips.innerHTML = "Click  <i class='fa fa-crosshairs fa-lg'></i> to search for a point by location name";
       
    }
    else if (step === 5) {
      
        tips.innerHTML = "Click <i class='fa fa-search-plus fa-lg'></i> when you want to make the image bigger";
       
    }
    else if (step === 6) {
    
        tips.innerHTML = "Click <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";
 
    }
    else if (step === 7) {
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image.";
    }
    else if (step === 8) {
    
        tips.innerHTML = "Click <i class='fa fa-save fa-lg'></i> to save when you are done inputing the coordinates";
 
    }
    else if (step === 9) {
        tips.innerHTML = "Click <i class='fas fa-play fa-lg'></i> after you have saved the coordinates and want to play the animation";
    }
    

    else if (step === 10) {
        closeTutorial();
    }
    

}

//refactor nisto
function goBack() {
    step--;
  
    if (step === 1) {
      goback.style.color = "transparent";
      tips.innerHTML = "Click <i class='fa fa-image fa-lg'></i> to open tan available image";

    }
    else if (step === 2) {
   
        tips.innerHTML = "Click <i class='fa fa-map-marker-alt fa-lg' ></i> to input the geographic coordinates";
      
    }
    else if (step === 3) {
      
        tips.innerHTML = "Click <i class='fa fa-undo fa-lg'></i> if you want to delete the last coordinate inputed";

    }
    else if (step === 4) {
    
        tips.innerHTML = "Click  <i class='fa fa-crosshairs fa-lg'></i> to search for a point by location name";
       
    }
    else if (step === 5) {
      
        tips.innerHTML = "Click <i class='fa fa-search-plus fa-lg'></i> when you want to make the image bigger";
       
    }
    else if (step === 6) {
    
        tips.innerHTML = "Click <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";
 
    }
    else if (step === 7) {
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image.";
    }
    else if (step === 8) {
    
        tips.innerHTML = "Click <i class='fa fa-save fa-lg'></i> to save when you are done inputing the coordinates";
 
    }
    else if (step === 9) {
        tips.innerHTML = "Click <i class='fas fa-play fa-lg'></i> after you have saved the coordinates and want to play the animation";
    }
    

    else if (step === 10) {
        closeTutorial();
    }

}