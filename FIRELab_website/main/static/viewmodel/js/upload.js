$(document).ready(function () {

    document.querySelectorAll('#file-upload__button').forEach(function (button) {
        const hiddenInput = button.parentElement.querySelector('.file-upload__input');
        const label = button.parentElement.querySelector('.file-upload__label');
        const labelImg = button.parentElement.querySelector('.file-upload__label-img');
        const defaultLabelText = 'No file selected';
        const uploadbutton = document.getElementById("submit_bt");
        const uploadbuttonVideo = document.getElementById("submit_vd");
        const inputFrames = document.getElementById("nrFramesInput");
        var nrframes = null;

        // Set default text for label
        label.textContent = defaultLabelText;
        label.title = defaultLabelText;

        button.addEventListener('click', function(){
            hiddenInput.click();
        });

        hiddenInput.addEventListener('change', function(){
            
            const fileName = Array.from(hiddenInput.files).map(function(file) {
                var videoExtensions = ["webm", "mpg", "mp2", "mpeg", "mpe", "mpv", "mp4", "m4p", "m4v", "ogg", "avi"];
                var imageExtensions = ["bmp", "tif", "jpg", "jpeg", "png", "eps", "tiff", "raw", "cr2", "nef", "orf", "sr2"];

                var fileExtension = file.name.substring(file.name.lastIndexOf('.')+1, file.name.length);
                if (document.getElementById("uploadVeg") != null) {
                  if (fileExtension == 'tif') {
                    if (document.getElementById("ortophoto").files[0].size * 9.31*Math.pow(10, -10) > 1) {
                        openWarningPopUp("Sorry, that type file is too big. Compress the file before you upload it. Tip: You can use GDAL to achieve this.");
                    }
                    else {
                        uploadbutton.style.display = "block";
                    }
                    
                  }
                  else {
                    openWarningPopUp("Sorry, that type of file is not permited. Choose a file with 'tif' extension.");
                  }
                }
                else if (document.getElementById("uploadSeg") != null) {
                    var inputValue;
                    let dateTime = new RegExp(".*?\[0-9\]{4}-(0\[1-9\]|1\[0-2\])-(0\[1-9\]|\[1-2\]\[0-9\]|3\[0-1\]) (2\[0-3\]|\[01\]\[0-9\]):\[0-5\]\[0-9\]:\[0-5\]\[0-9\]");
                    if (videoExtensions.includes(fileExtension.toLowerCase())) {
                        document.getElementById("startingDateTime").style.display = "flex";
                        console.log(nrframes);
                         $("#startingDateTime, #nrFramesInput").on("input", function(){
                            inputValue = document.getElementById("id_startingDateTime").value;
                            nrframes = inputFrames.value;
                            console.log(nrframes);
                            var dateInput = inputValue.split(" ")[1];   
                            var stDate = document.getElementById("startingTimestamp").innerText.split(" ")[6];
                            var edDate = document.getElementById("endingTimestamp").innerText.split(" ")[6];

                            if (inputValue.match(dateTime)) {
                               if (stDate <= dateInput && edDate >= dateInput && nrframes != 'undefined' && nrframes != null && nrframes != "") {
                                uploadbuttonVideo.style.display = "block"; 
                               }
                               else {
                                uploadbuttonVideo.style.display = "none";
                               }
                            }
                            else {
                                uploadbuttonVideo.style.display = "none";
                            }                   
                        });
                        
                    }
                
                    else if (imageExtensions.includes(fileExtension.toLowerCase())) {
                        uploadbutton.style.display = "block";
                    }
                    else {
                        openWarningPopUp("Sorry, that type of file is not permited. Choose a file of the correct format.");
                    }
                }
                //uploadbutton.style.display = "block";
                return file.name;
            });

            label.textContent = fileName || defaultLabelText;
            label.title = label.textContent;

        });

    });


});

const loadingPopUp = document.getElementById("waiting");
const blur = document.getElementById("blur");

function openLoadingPopUp() {
    loadingPopUp.style.display = "flex";
    blur.style.filter = "blur(2px)";
}

function openWarningPopUp(msg) {
    const element = document.getElementById("msg");
    element.innerHTML = msg;
    warning_popup.style.display = "flex";
    blur.style.filter = "blur(2px)";
    setTimeout(function() { closePopUp(); }, 5000);
}

function closePopUp() {
    warning_popup.style.display = "none";
    blur.style.filter = "none";
}