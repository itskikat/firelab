
var blur = document.getElementById("blur");

function openForm() {
  document.getElementById("myForm").style.display = "block";
  blur.style.filter = "blur(2px)";

}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
  blur.style.filter = "none";
}


function openCheckDelete() {
  document.getElementById("deleteCheck").style.display = "block";
  blur.style.filter = "blur(2px)";

}

function closeDelete() {
  document.getElementById("deleteCheck").style.display = "none";
  blur.style.filter = "none";
}


function openChangePassword() {
	document.getElementById("passwordChange").style.display = "block";
  	blur.style.filter = "blur(2px)";
}

function closeFormPassword() {
  document.getElementById("passwordChange").style.display = "none";
  blur.style.filter = "none";
}


function openChangeEmail() {
	document.getElementById("changeEmail").style.display = "block";
  	blur.style.filter = "blur(2px)";
}

function closeFormEmail() {
  document.getElementById("changeEmail").style.display = "none";
  blur.style.filter = "none";
}


var hexPicker = document.getElementById("typeColor");
var hexColor = document.getElementById("id_hexColor");

hexPicker.addEventListener('input', function(){
           
            hexColor.value = hexPicker.value.replace("#", "");
        });

hexColor.addEventListener('input', function(){
           
            hexPicker.value = '#' + hexColor.value;
        });

