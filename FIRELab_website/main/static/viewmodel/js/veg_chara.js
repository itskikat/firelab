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