import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const init = readFileSync(
  new URL("./reads_theme_init.js", import.meta.url),
  "utf8",
);
const script = readFileSync(
  new URL("./reads_theme.js", import.meta.url),
  "utf8",
);

function page(storage = new Map(), blocked = false, ready = "complete") {
  const classes = new Set();
  const attrs = new Map();
  const clicks = new Map();
  const events = new Map();
  const documentEvents = new Map();
  const root = {
    dataset: {},
    classList: {
      contains: (name) => classes.has(name),
      toggle(name, on) {
        if (on) classes.add(name);
        else classes.delete(name);
      },
    },
  };
  const button = {
    hidden: true,
    setAttribute: (name, value) => attrs.set(name, value),
    addEventListener: (name, handler) => clicks.set(name, handler),
  };
  const sandbox = {
    document: {
      documentElement: root,
      readyState: ready,
      querySelectorAll: () => [button],
      addEventListener: (name, handler) => documentEvents.set(name, handler),
    },
    window: { addEventListener: (name, handler) => events.set(name, handler) },
    localStorage: {
      getItem(key) {
        if (blocked) throw new Error("Storage denied");
        return storage.get(key) ?? null;
      },
      setItem(key, value) {
        if (blocked) throw new Error("Storage denied");
        storage.set(key, value);
      },
    },
  };
  vm.runInNewContext(init, sandbox);
  const beforeBoot = root.classList.contains("dark");
  vm.runInNewContext(script, sandbox);
  return {
    root,
    button,
    attrs,
    storage,
    beforeBoot,
    click: () => clicks.get("click")(),
    storageChanged: (key = "spk-theme") => events.get("storage")({ key }),
    pageShown: () => events.get("pageshow")(),
    domReady: () => documentEvents.get("DOMContentLoaded")(),
  };
}

test("new visitors start light with an accessible theme control", () => {
  const p = page();
  assert.equal(p.beforeBoot, false);
  assert.equal(p.root.dataset.readsColorMode, "light");
  assert.equal(p.button.hidden, false);
  assert.equal(p.attrs.get("aria-label"), "어두운 테마");
  assert.equal(p.attrs.get("aria-pressed"), "false");
});

test("saved dark mode applies before the controls boot", () => {
  const p = page(new Map([["spk-theme", "dark"]]), false, "loading");
  assert.equal(p.beforeBoot, true);
  assert.equal(p.button.hidden, true);
  p.domReady();
  assert.equal(p.attrs.get("aria-pressed"), "true");
  assert.equal(p.button.textContent, "☾ 다크");
});

test("home -> blog -> article -> news -> home shares one preference", () => {
  const storage = new Map();
  const home = page(storage);
  home.click();
  assert.equal(storage.get("spk-theme"), "dark");
  for (const name of [
    "blog",
    "blog article",
    "news",
    "news article",
    "refreshed home",
  ]) {
    assert.equal(page(storage).root.classList.contains("dark"), true, name);
  }
  const article = page(storage);
  article.click();
  assert.equal(page(storage).root.classList.contains("dark"), false);
  assert.equal(storage.get("spk-theme"), "light");
});

test("a preference change in another tab and cleared storage synchronize", () => {
  const storage = new Map();
  const p = page(storage);
  storage.set("spk-theme", "dark");
  p.storageChanged();
  assert.equal(p.attrs.get("aria-pressed"), "true");
  storage.clear();
  p.storageChanged(null);
  assert.equal(p.attrs.get("aria-pressed"), "false");
});

test("blocked storage does not break the theme button", () => {
  const p = page(new Map(), true);
  assert.doesNotThrow(() => p.click());
  assert.equal(p.root.classList.contains("dark"), true);
  p.click();
  assert.equal(p.root.classList.contains("dark"), false);
});

test("a page restored by browser back/forward rereads the selected mode", () => {
  const storage = new Map([["spk-theme", "dark"]]);
  const cached = page(storage);
  storage.set("spk-theme", "light");
  cached.pageShown();
  assert.equal(cached.root.classList.contains("dark"), false);
  assert.equal(cached.attrs.get("aria-pressed"), "false");
});

test("unknown preferences fall back to light", () => {
  assert.equal(
    page(new Map([["spk-theme", "unknown"]])).root.dataset.readsColorMode,
    "light",
  );
});
