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
	var upload = document.getElementById("uploadVeg"); 
	if ( window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
    } else {
        upload.style.display = 'none';
    }
}


function openClosePicker() {
	var picker = document.getElementById("pickerBody");
	var icon = document.getElementById("closeP");
	var cp = document.getElementById("closePicker");
	var caption = document.getElementById("captionPicker");

	if (picker.style.display === "none") {
		icon.className = "fas fa-times";
		picker.style.display = "block";
		icon.style.padding = "0 0 0 70%";
		caption.style.padding = "0";
		cp.title = "Close Picker";
	}

	else {
		picker.style.display = "none";
		icon.className = "fas fa-angle-down";
		icon.style.padding = "0 0 0 15%";
		caption.style.padding = "0 0 0 62%";
		cp.title = "Open Picker";

	}
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
   tips.innerHTML = "Click <i class='fas fa-folder-open fa-lg' ></i> here to upload an orthophotomap";
  
 
}

function next() {
  goback.style.color = "#E4C3B1";
    step++;
    console.log(step);
    if (step === 1) {
       tips.innerHTML = "Click <i class='fa fa-border-all fa-lg' ></i> and mark two points in the map to create a grid";
      tutorial.classList.remove("stepZero");
    }
    if (step === 2) {
      
      tips.innerHTML = "Click <i class='fa fa-leaf fa-lg'></i> and characterize a few cells by clicking on a color in the table below and picking one or various cells. You can set the size of the brush in the bar next to the toolkit";

    }
    else if (step === 3) {
   
        tips.innerHTML = "Click <i class='fas fa-tree fa-lg' ></i> to automatically characterize the vegetation";
      
    }
    
    else if (step === 4) {
    
        tips.innerHTML = "Click  <i class='fa fa-search-plus fa-lg'></i> when you want to make the image bigger";
       
    }
    else if (step === 5) {
      
        tips.innerHTML = "Click <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";
       
    }
    else if (step === 6) {
  
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image";
 
    }
    else if (step === 7) {
        tips.innerHTML = "Click <i class='fas fa-save fa-lg'></i> when you are done and want to save the results";
    }

    else if (step === 8) {
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
      tips.innerHTML = "Click <i class='fas fa-folder-open fa-lg' ></i> here to upload an orthophotomap";
    }
    if (step === 1) {
      tips.innerHTML = "Click <i class='fa fa-border-all fa-lg' ></i> and mark two points in the map to create a grid";
    }
    if (step === 2) {
      tips.innerHTML = "Click <i class='fa fa-leaf fa-lg'></i> and characterize a few cells by clicking on a color in the table below and picking one or various cells. You can set the size of the brush in the bar next to the toolkit";

    }
    else if (step === 3) {
        tips.innerHTML = "Click <i class='fas fa-tree fa-lg' ></i> to automatically characterize the vegetation";
     
    }
    else if (step === 4) {
        tips.innerHTML = "Click  <i class='fa fa-search-plus fa-lg'></i> when you want to make the image bigger";
      
    }
    else if (step === 5) {
        tips.innerHTML = "Click <i class='fa fa-search-minus fa-lg'></i> when you want to make the image smaller";

    }
    else if (step === 6) {
        tips.innerHTML = "Click <i class='fas fa-expand-arrows-alt fa-lg'></i> when you want to resize the image";
 
    }
    else if (step === 7) {
      tips.innerHTML = "Click <i class='fas fa-save fa-lg'></i> when you are done and want to save the results";
    }
    else if (step === 8) {
      tips.innerHTML = "Click <i class='fas fa-save fa-lg'></i> when you are done and want to save the results.";
    }

}


function openColorPicker() {
  document.getElementById("colorPicker").style.display = "flex";
}


function openColorPicker() {
  document.getElementById("colorPicker").style.display = "flex";
}

function closeColorPicker() {
  document.getElementById("colorPicker").style.display = "none";
}

function closeGridPopUp() {
  document.getElementById("createGridHelp").style.display = "flex";
  document.getElementById("gridPop").style.display = "none";
}