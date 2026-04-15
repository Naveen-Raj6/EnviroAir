/**
 * EnviroAir — client-side helpers for the data preview page.
 * Loaded only from templates/preview.html (see url_for('static', filename='js/script.js')).
 */

(function () {
  "use strict";

  // Floating control: scrolls the page to the bottom (useful on long CSV tables).
  var backToBottomBtn = document.getElementById("backToBottomBtn");

  // If the button is not on this page, do nothing (other routes do not include it).
  if (!backToBottomBtn) {
    return;
  }

  /**
   * Show the button when the user is not near the bottom of the page;
   * hide it when they are already at the bottom.
   */
  function scrollFunction() {
    var nearBottom =
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
    if (nearBottom) {
      backToBottomBtn.classList.add("hidden");
    } else {
      backToBottomBtn.classList.remove("hidden");
    }
  }

  window.addEventListener("scroll", scrollFunction);
  scrollFunction();

  // Smooth scroll to the end of the document when the button is clicked.
  backToBottomBtn.addEventListener("click", function () {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  });
})();
