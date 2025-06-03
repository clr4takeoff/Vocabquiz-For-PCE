document.addEventListener("DOMContentLoaded", function () {
  if (window.fromCheckPage) {
    document.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        const nextForm = document.getElementById("nextForm");
        if (nextForm) {
          nextForm.submit();
        }
      }
    });
  }
});

console.log("main.js loaded");
