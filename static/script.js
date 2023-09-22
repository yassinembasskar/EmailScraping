

var collapse = document.getElementById("navbarNav");
var result_section = document.getElementById("result_section");
var details_section = document.getElementById("details_section");

var images_container_position = 0;
var images_container = document.getElementById("images_container");

function navAction(){

    var computedStyle = window.getComputedStyle(collapse);
    var displayValue = computedStyle.getPropertyValue('display');
    console.log(displayValue);
    if(displayValue == "none"){
        collapse.style.display = "block";
    } else {
        collapse.style.display = "none";
    }
}

function show_details(){
    result_section.style.display = "none";
    details_section.style.display = "flex";
}

function hide_details(){
    result_section.style.display = "flex";
    details_section.style.display = "none";
}


