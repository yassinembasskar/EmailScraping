

var collapse = document.getElementById("navbarNav");
var result_section = document.getElementById("result_section");
var details_section = document.getElementById("details_section");
var details_section = document.getElementById("details_section_2");

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

function show_details_2(){
    result_section.style.display = "none";
    details_section_2.style.display = "flex";
}

function hide_details_2(){
    result_section.style.display = "flex";
    details_section_2.style.display = "none";
}

function next(){
    if (images_container_position < 5){
        images_container_position += 1;
    }
    images_container.style.transform = "translateX(calc("+ -1/6 * images_container_position +"*100%))";
}

function previous(){
    if (images_container_position > 0){
        images_container_position -= 1;
    }
    images_container.style.transform = "translateX(calc("+ -1/6 * images_container_position +"*100%))";
}