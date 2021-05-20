$(document).ready(function () {

    document.querySelectorAll('#file-upload__button').forEach(function (button) {
        const hiddenInput = button.parentElement.querySelector('.file-upload__input');
        const label = button.parentElement.querySelector('.file-upload__label');
        const defaultLabelText = 'No file selected';
        const uploadbutton = document.getElementById("submit_bt")
        const uploadbuttonVideo = document.getElementById("submit_vd")

        // Set default text for label
        label.textContent = defaultLabelText;
        label.title = defaultLabelText;

        button.addEventListener('click', function(){
            hiddenInput.click();
        });

        hiddenInput.addEventListener('change', function(){
            // console.log(hiddenInput.files);
            const fileName = Array.from(hiddenInput.files).map(function(file) {
                uploadbutton.style.display = "block";
                uploadbuttonVideo.style.display = "block";
                return file.name;
            });
            // console.log(fileName);

            label.textContent = fileName || defaultLabelText;
            label.title = label.textContent;

        });

    });



});

const loadingPopUp = document.getElementById("waiting");
const blur = document.getElementById("blur");

function openLoadingPopUp() {
    loadingPopUp.style.display = "flex";
    blur.style.filter = "blur(2px)"
}