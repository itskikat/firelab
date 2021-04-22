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
	if ( window.getComputedStyle(upload, null).getPropertyValue("display") === 'none') {
        upload.style.display = 'block';
    } else {
        upload.style.display = 'none';
    }
	
}