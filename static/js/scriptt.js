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
document.addEventListener("DOMContentLoaded", function () {
    const particleContainer = document.querySelector(".particle-container");

    function createParticle() {
        const particle = document.createElement("div");
        particle.classList.add("particle");

        // Random start position
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;

        // Random movement direction
        particle.style.setProperty("--x", `${Math.random() * 200 - 100}px`);
        particle.style.setProperty("--y", `${Math.random() * 200 - 100}px`);

        particleContainer.appendChild(particle);

        // Remove particle after animation
        setTimeout(() => {
            particle.remove();
        }, 5000);
    }

    // Generate multiple particles over time
    setInterval(createParticle, 300);
});

