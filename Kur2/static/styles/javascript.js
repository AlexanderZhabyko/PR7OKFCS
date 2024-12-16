document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".user-box input");

    inputs.forEach(input => {
        input.addEventListener("focus", () => {
            inputs.forEach(field => field.classList.add("autofill-visible"));
        });
    });
});