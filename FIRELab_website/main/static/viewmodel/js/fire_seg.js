var img_seg = document.getElementById("img_seg");
var x = 1.1;
var search_plus = document.getElementById("search_plus");

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
        // img_seg.style.display = 'none';
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

$("#maskToggle").click(function (event) {
    maskOn = !maskOn;
});


//var blur = '#{{ blur }}';
const saveFile = document.getElementById("saveFile");

function save() {
  saveFile.style.display = "block";
  //blur.style.filter = "blur(2px)";
  saveFile.style.filter = "none";

}

function closeSave() {
  saveFile.style.display = "none";
}

const closeTi = document.getElementById("closeTimeline");
const closeT = document.getElementById("closeT");
const timeline = document.getElementById("timeline");
const frameTable = document.getElementById("frameTable");
const here = document.getElementById("open");

function closeTimeline() {
    timeline.style.display = 'none';
    here.style.display = 'flex';

}

function openTimeline() {
    timeline.style.display = 'block';
    here.style.display = 'none';
}