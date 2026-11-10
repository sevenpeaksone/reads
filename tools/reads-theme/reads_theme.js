(function () {
  var root = document.documentElement;
  var key = "spk-theme";

  function readMode() {
    try {
      return localStorage.getItem(key) === "dark" ? "dark" : "light";
    } catch (error) {
      return root.dataset.readsColorMode === "dark" ? "dark" : "light";
    }
  }

  function boot() {
    var buttons = document.querySelectorAll(
      "[data-reads-theme-toggle], #theme-toggle",
    );

    function apply(mode, save) {
      var dark = mode === "dark";
      root.classList.toggle("dark", dark);
      root.dataset.readsColorMode = dark ? "dark" : "light";
      buttons.forEach(function (button) {
        button.hidden = false;
        button.setAttribute("aria-label", "어두운 테마");
        button.setAttribute("aria-pressed", String(dark));
        button.title = dark ? "밝은 테마로 전환" : "어두운 테마로 전환";
        button.textContent = dark ? "☾ 다크" : "☀ 라이트";
      });
      if (save) {
        try {
          localStorage.setItem(key, dark ? "dark" : "light");
        } catch (error) {
          // Keep the current page usable even when persistence is blocked.
        }
      }
    }

    apply(readMode(), false);
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        apply(root.classList.contains("dark") ? "light" : "dark", true);
      });
    });
    window.addEventListener("storage", function (event) {
      if (event.key === key || event.key === null) apply(readMode(), false);
    });
    window.addEventListener("pageshow", function () {
      apply(readMode(), false);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
