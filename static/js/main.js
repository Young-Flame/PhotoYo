"use strict";

// Set class active to burger menu button and mobile menu list
// Toggle button to show and hide burger menu
function toggleBurgerMenu() {
    const menuButton = document.querySelector(".burger-menu");
    const mobileMenu = document.querySelector(".mobile-menu");

    menuButton.addEventListener("click", function () {
        menuButton.classList.toggle("active");
        mobileMenu.classList.toggle("active");
    })

    menuButton.addEventListener("click", function () {
        let hidden = mobileMenu.getAttribute("hidden");
        if (hidden) {
            mobileMenu.removeAttribute("hidden")
        } else {
            mobileMenu.setAttribute("hidden", "hidden")
        }
    })
};

toggleBurgerMenu();

//  Set active class to current navigation a
function setActiveLink() {
    const menuLinks = document.querySelectorAll(".nav a");
    let currentURL = window.location.href;
    for (let link of menuLinks) {
        if (link.href === currentURL) {
            link.classList.add("active")
        }
    }
};

setActiveLink();

// Failure button redirect login page
function refreshLoginPage() {
    const failureButton = document.querySelector(".failure-button")
    if (!failureButton) {
        return;
    }
    failureButton.addEventListener("click", function () {
        location.replace(location.href);
    })
};

refreshLoginPage();

// On image click diplay full size photo
function fullSizeImage() {
    document.querySelectorAll(".gallery-grid img").forEach(image => {
        image.onclick = () => {
            document.querySelector(".full-size-photo").style.display = "block";
            document.querySelector(".full-size-photo img").src = image.getAttribute("src");
        }
    })
};

fullSizeImage();

function closeImage() {
    // On span click display full size photo style to none
    document.querySelector(".full-size-photo span").onclick = () => {
        document.querySelector(".full-size-photo").style.display = "none";
    };
    // Keypress esc for display full size photo style to none
    document.addEventListener("keydown",function(e){
        if(e.key === "Escape") {
            document.querySelector(".full-size-photo").style.display = "none";
        }
    });
};

closeImage();




