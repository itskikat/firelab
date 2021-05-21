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
