// Mobile Menu Toggle - Simple and Reliable
(function() {
    'use strict';
    
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (!hamburger || !navMenu) return;
    
    // Simple toggle function
    function toggleMenu() {
        const isActive = navMenu.classList.contains('active');
        if (isActive) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        } else {
            navMenu.classList.add('active');
            hamburger.classList.add('active');
        }
    }
    
    // Handle click
    hamburger.onclick = function(e) {
        e.stopPropagation();
        toggleMenu();
    };
    
    // Handle touch for mobile
    hamburger.ontouchstart = function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    };
    
    // Close menu when clicking links
    const links = navMenu.querySelectorAll('a');
    for (let i = 0; i < links.length; i++) {
        links[i].onclick = function() {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        };
    }
    
    // Close when clicking outside
    document.onclick = function(e) {
        if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    };
})();
