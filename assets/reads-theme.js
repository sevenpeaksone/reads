(function () {
  function lightOnly() {
    var root = document.documentElement;
    root.classList.remove("dark");
    root.dataset.readsColorMode = "light";
    root.style.colorScheme = "light";
    document.querySelectorAll("[data-reads-theme-toggle], #theme-toggle").forEach(function (button) {
      button.remove();
    });
    try {
      localStorage.removeItem("spk-theme");
    } catch (error) {
      // Preserve search, saved articles, view preferences, and reading state.
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", lightOnly, { once: true });
  } else {
    lightOnly();
  }
  window.addEventListener("pageshow", lightOnly);
  window.addEventListener("storage", function (event) {
    if (event.key === "spk-theme" || event.key === null) lightOnly();
  });
})();
