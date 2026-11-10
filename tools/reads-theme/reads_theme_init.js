(function () {
  var mode = "light";
  try {
    if (localStorage.getItem("spk-theme") === "dark") mode = "dark";
  } catch (error) {
    // Storage may be unavailable in a restricted browsing context.
  }
  var root = document.documentElement;
  root.classList.toggle("dark", mode === "dark");
  root.dataset.readsColorMode = mode;
})();
