(function () {
  var root = document.documentElement;
  root.classList.remove("dark");
  root.dataset.readsColorMode = "light";
  root.style.colorScheme = "light";
  try {
    localStorage.removeItem("spk-theme");
  } catch (error) {
    // Light presentation also works when browser storage is unavailable.
  }
})();
