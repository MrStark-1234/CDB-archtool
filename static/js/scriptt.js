document.addEventListener("DOMContentLoaded", function () {
    // Select the Solution button
    const solutionBtn = document.querySelector('nav ul li a[href="#solution"]');

    if (solutionBtn) {
        solutionBtn.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior

            // Scroll smoothly to the Solution section
            document.querySelector("#solution").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    }
});
