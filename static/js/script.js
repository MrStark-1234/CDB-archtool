document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file-upload");
    const progressFill = document.querySelector(".progress-fill");
    const sidebarLinks = document.querySelectorAll(".sidebar ul li a");

    // Handle Sidebar Clicks
    sidebarLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent default anchor behavior
            const targetId = this.getAttribute("href").substring(1); // Get the section ID
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    // Simulate File Upload Progress
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            simulateProgress();
        }
    });

    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressFill.style.width = `${progress}%`;
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 300);
    }

    // Active Link Highlight on Scroll
    window.addEventListener("scroll", () => {
        let current = "";
        document.querySelectorAll("section").forEach((section) => {
            const sectionTop = section.offsetTop;
            if (window.scrollY >= sectionTop - 50) {
                current = section.getAttribute("id");
            }
        });

        sidebarLinks.forEach((link) => {
            link.parentElement.classList.remove("active");
            if (link.getAttribute("href").substring(1) === current) {
                link.parentElement.classList.add("active");
            }
        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const sidebarLinks = document.querySelectorAll(".sidebar ul li a");

    // Smooth Scroll when clicking sidebar links
    sidebarLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent default jump behavior

            const targetId = this.getAttribute("href").substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });

    // Highlight active sidebar link on scroll
    window.addEventListener("scroll", () => {
        let current = "";
        document.querySelectorAll("section").forEach((section) => {
            const sectionTop = section.offsetTop;
            if (window.scrollY >= sectionTop - 50) {
                current = section.getAttribute("id");
            }
        });

        sidebarLinks.forEach((link) => {
            link.parentElement.classList.remove("active");
            if (link.getAttribute("href").substring(1) === current) {
                link.parentElement.classList.add("active");
            }
        });
    });
});
