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
   if (tutorial.className === "tooltip-wrapper stepZero noImg") {
    step = 0;
   }
}

function closeTutorial() {
   tutorial.style.display = "none";
   tutorial.classList.remove(className);
   tips.innerHTML = "Click here and select the image";
   console.log(tutorial.className);
   if (tutorial.className === "tooltip-wrapper noImg" || tutorial.className === "tooltip-wrapper stepZero noImg") {
    step = 0;
    tutorial.classList.add("stepZero");
   }
   else {
    step = 1;
   }
}

function next() {
  goback.style.color = "#E4C3B1";
    step++;
    console.log(step);
    if (step === 1) {
       tips.innerHTML = "Click here to select two points in the image to make a grid";
      tutorial.classList.add("first"); 
      tutorial.classList.remove("stepZero");
      className = "first";  
    }
    if (step === 2) {
      tips.innerHTML = "Click here to do the characterization automatically";
      tutorial.classList.add("second"); 
      tutorial.classList.remove("first");
      className = "second"; 
    }
    else if (step === 3) {
        tutorial.classList.remove("second"); 
        tips.innerHTML = "Click here to select a square from the grid";
       tutorial.classList.add("third");   
       className = "third";
    }
    else if (step === 4) {
        tutorial.classList.remove("third"); 
        tips.innerHTML = "Click here to erase any color of a certain square";
       tutorial.classList.add("fourth");   
       className = "fourth";
    }
    else if (step === 5) {
        tutorial.classList.remove("fourth"); 
        tips.innerHTML = "Click here when you want to make the image bigger";
       tutorial.classList.add("fifth");   
       className = "fifth";
    }
    else if (step === 6) {
        tutorial.classList.remove("fifth"); 
        tips.innerHTML = "Click here when you want to make the image smaller";
        className = "sixth";
       tutorial.classList.add("sixth");   
    }
    else if (step === 7) {
        tutorial.classList.remove("sixth"); 
        tips.innerHTML = "Click here when you want to move the image";
        className = "seventh";
       tutorial.classList.add("seventh");   
    }
    else if (step === 8) {
        tutorial.classList.remove(className); 
        tips.innerHTML = "Click here when you are done and want to save the image";
        className = "eight";
       tutorial.classList.add("eight");   
    }
    
}

function goBack() {
    step--;
    tutorial.classList.remove(className);
    console.log(tutorial.classList);
    console.log(step);
    if (step === 0 || (step === 1 && !tutorial.classList.contains('noImg'))) {
        goback.style.color = "transparent";
        console.log("oi");
    }
    if (step === 0) {
      tips.innerHTML = "Click here to upload a video or image";
      tutorial.classList.add("stepZero"); 
      className = "stepZero";
    }
    if (step === 1) {
      tips.innerHTML = "Click here and select the image to segment";
      tutorial.classList.add("first"); 
      tutorial.classList.remove("stepZero");
      className = "first";  
    }
    if (step === 2) {
      tips.innerHTML = "Click here to start selecting the burnt area";
      tutorial.classList.add("second"); 
      tutorial.classList.remove("first");
      className = "second"; 
    }
    else if (step === 3) {
        tutorial.classList.remove("second"); 
        tips.innerHTML = "Click here when you want to unselect some area";
       tutorial.classList.add("third");   
       className = "third";
    }
    else if (step === 4) {
        tutorial.classList.remove("third"); 
        tips.innerHTML = "Click here when you want to make the image bigger";
       tutorial.classList.add("fourth");   
       className = "fourth";
    }
    else if (step === 5) {
        tutorial.classList.remove("fourth"); 
        tips.innerHTML = "Click here when you want to make the image smaller";
       tutorial.classList.add("fifth");   
       className = "fifth";
    }
    else if (step === 6) {
        tutorial.classList.remove("fifth"); 
        tips.innerHTML = "Click here when you want to move the image";
        className = "sixth";
       tutorial.classList.add("sixth");   
    }
    else if (step === 7) {
        tutorial.classList.remove("sixth"); 
        tips.innerHTML = "Click here when you are done and want to save the image.";
        className = "seventh";
       tutorial.classList.add("seventh");   
    }

}