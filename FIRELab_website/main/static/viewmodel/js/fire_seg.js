img_seg = document.getElementById("img_seg");
var x = 1.1;
var search_plus = document.getElementById("search_plus");

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


function openUpload() {
    console.log("oi");
    var upload = document.getElementById("uploadSeg");
    if ( window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
        img_seg.style.display = 'none';
    } else {
        upload.style.display = 'none';
        img_seg.style.display = 'flex';
    }

}

function enlargeImg() {

    if (x == 1.0) {
    x = x + 0.1;
}
else {
    x = x + 0.2;
}
img_seg.style.transform = "scale(" + x + ")";
img_seg.style.transition = "transform 0.25s ease";

}

function imgSmall() {
if (x == 1.1) {
    x = x - 0.1;
    img_seg.style.transform = "scale(" + x + ")";
    img_seg.style.transition = "transform 0.25s ease";
}
else if (x > 1.1) {
    x = x - 0.2;
    img_seg.style.transform = "scale(" + x + ")";
    img_seg.style.transition = "transform 0.25s ease";

}

}

function penOn() {
    $("#id_pen").attr('checked', true);
    $("#id_eraser").attr('checked', false);
    $("#pen").css("color", "#B55B29")
    $("#eraser").css("color", "")
}

function penOff() {
    $("#id_pen").attr('checked', false);
    $("#id_eraser").attr('checked', true);
    $("#pen").css("color", "")
    $("#eraser").css("color", "#B55B29")
}


//var blur = '#{{ blur }}';
saveFile = document.getElementById("saveFile");

function save() {
  saveFile.style.display = "block";
  //blur.style.filter = "blur(2px)";
  saveFile.style.filter = "none";

}

function closeSave() {
  saveFile.style.display = "none";
}

closeTi = document.getElementById("closeTimeline");
closeT = document.getElementById("closeT");
 timeline = document.getElementById("timeline");
 frameTable = document.getElementById("frameTable");
 here = document.getElementById("open");

function closeTimeline() {
    timeline.style.display = 'none';
    here.style.display = 'flex';
    $("#img_seg").css("padding-top", "14vh")

}

function openTimeline() {
    timeline.style.display = 'block';
    here.style.display = 'none';
    $("#img_seg").css("padding-top", "6vh")
}



//TUTORIAL

const tutorial = document.getElementById("tutorial");
const tips = document.getElementById("tips");
const goback = document.getElementById("goBack");

var step = 1;
var className;

function openTutorial() {
    
  goback.style.color = "transparent";
    console.log(tutorial.className);
   tutorial.style.display = "flex";
  
}

function closeTutorial() {
   tutorial.style.display = "none";
   step = 0;
   tips.innerHTML = "Click <i class='fas fa-folder-open fa-lg' ></i> here to upload a video or image";
  
 
}

function next() {
  goback.style.color = "#E4C3B1";
    step++;
    console.log(step);
    if (step === 1) {
 
       tips.innerHTML = "Click <i class='fa fa-fire-extinguisher fa-lg' ></i> and select the points of no interest in the image";
      tutorial.classList.remove("stepZero");
    }
    if (step === 2) {
      
      tips.innerHTML = "Click <i class='fa fa-fire fa-lg'></i> to start selecting the burnt area in the image";

    }
    else if (step === 3) {
   
        tips.innerHTML = "Click <i class='fa fa-fire-extinguisher fa-lg' ></i> when you want to unselect some area in the image";
      
    }
    else if (step === 4) {
      
        tips.innerHTML = "Click <i class='fa fa-search-plus fa-lg'></i>  when you want to make the image bigger";

    }
    else if (step === 5) {
    
        tips.innerHTML = "Click  <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";
       
    }
    else if (step === 6) {
      
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image";
       
    }
    else if (step === 8) {
        tips.innerHTML = "Click <i class='fas fa-save fa-lg'></i> when you are done and want to save the image";
 
    }
    else if (step === 7) {
        if (document.getElementById('imgMask') != null) {
      tips.innerHTML = "Click <i class='fas fa-eye fa-lg'></i> if you want to toggle the mask. The icon should appear when you start segmentating.";
        }
        
    }

    else if (step === 9) {
        closeTutorial();
    }
    

}

//refactor nisto
function goBack() {
    step--;
  
    if (step === 0 || (step === 1 && !tutorial.classList.contains('noImg'))) {
        goback.style.color = "transparent";
        
    }
    if (step === 0) {
      tips.innerHTML = "Click <i class='fas fa-folder-open fa-lg' ></i> here to upload a video or image";
    }
    if (step === 1) {
      tips.innerHTML = "Click <i class='fa fa-fire-extinguisher fa-lg' ></i> and select the points of no interest";   
    }
    if (step === 2) {
      tips.innerHTML = "Click <i class='fa fa-fire fa-lg' ></i> to start selecting the burnt area";
    }
    else if (step === 3) {
        tips.innerHTML = "Click <i class='fa fa-fire-extinguisher fa-lg' ></i> when you want to unselect some area";
     
    }
    else if (step === 4) {
        tips.innerHTML = "Click <i class='fa fa-search-plus fa-lg'></i>  when you want to make the image bigger";
   
    }
    else if (step === 5) {
        tips.innerHTML = "Click  <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";
      
    }
    else if (step === 6) {
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image";

    }
    else if (step === 8) {
        tips.innerHTML = "Click <i class='fas fa-save fa-lg'></i> when you are done and want to save the image";
 
    }
    else if (step === 7) {
        if (document.getElementById('imgMask') != null) {
      tips.innerHTML = "Click <i class='fas fa-eye fa-lg'></i> if you want to toggle the mask. The icon should appear when you start segmentating.";
        }
        
    }

    else if (step === 9) {
        closeTutorial();
    }

}