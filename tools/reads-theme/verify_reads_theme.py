"""Read-only checks for a staged Reads theme against its publishing baseline."""
import argparse
import ast
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class ArticleContent(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.suppressed = 0
        self.text = []
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "body":
            self.in_body = True
        if self.suppressed:
            if tag not in {"img", "br", "hr", "input", "meta", "link", "source", "wbr"}:
                self.suppressed += 1
            return
        if tag in {"head", "style", "script"} or attrs.get("id") in {
            "site-nav", "read-progress", "to-top"
        }:
            self.suppressed = 1
            return
        if self.in_body and tag == "img":
            self.images.append(attrs.get("src"))
        if self.in_body and tag == "a":
            self.links.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if self.suppressed:
            self.suppressed -= 1
        if tag == "body":
            self.in_body = False

    def handle_data(self, text):
        if self.in_body and not self.suppressed and text.strip():
            self.text.append(re.sub(r"\s+", " ", text).strip())


def content(text):
    if text.strip() and not re.search(r"<body\b", text, re.I):
        first = re.search(r"<(?:div|article|main)\b", text, re.I)
        assert first is not None, "Unrecognized legacy fragment"
        text = "<body>" + text[first.start():] + "</body>"
    parsed = ArticleContent()
    parsed.feed(text)
    return parsed.text, parsed.images, parsed.links


def verify(baseline, staged):
    counts = Counter()
    empty = []
    fragments = []
    errors = []
    for original in sorted(baseline.glob("*/*/*/index.html")):
        relative = original.relative_to(baseline)
        if relative.parts[0] not in {"posts", "news"}:
            continue
        counts[relative.parts[0]] += 1
        target = staged / relative
        if not target.exists():
            errors.append(f"Missing article: {relative}")
            continue
        old, new = original.read_text(), target.read_text()
        if not old.strip():
            empty.append(str(relative))
            if new != old:
                errors.append(f"Empty source changed: {relative}")
            continue
        if not re.search(r"<body\b", old, re.I):
            fragments.append(str(relative))
        if content(old) != content(new):
            errors.append(f"Article text/images/links changed: {relative}")
        for marker in ('id="site-nav"', 'id="site-chrome-css"', 'id="site-chrome-js"', 'data-reads-view="article"', 'id="reads-theme-init"', 'id="reads-theme-script"', 'id="theme-toggle"'):
            if new.count(marker) != 1:
                errors.append(f"Invalid marker count ({marker}): {relative}")
        if '<link id="site-chrome-css"' not in new or '/reads/assets/reads-theme.css?v=lime-v4' not in new:
            errors.append(f"Missing canonical design link: {relative}")
        if '<style id="site-chrome-css"' in new:
            errors.append(f"Legacy embedded chrome stylesheet: {relative}")
        if '/reads/assets/reads-theme.js?v=lime-v4' not in new:
            errors.append(f"Missing shared color-mode script: {relative}")
    if not sum(counts.values()):
        errors.append("No articles were checked")
    search_unchanged = json.loads((baseline / "search.json").read_text()) == json.loads((staged / "search.json").read_text())
    if not search_unchanged:
        errors.append("Search metadata changed")
    if (staged / "assets/7peaks-wordmark-light.svg").read_bytes() == b"":
        errors.append("Missing wordmark")
    stylesheet_matches_source = (staged / 'assets/reads-theme.css').read_bytes() == (
        staged / 'tools/reads-theme/reads_theme.css').read_bytes()
    if not stylesheet_matches_source:
        errors.append("Published stylesheet does not match its canonical source")
    script_names = {"SEARCH_JS", "PREFS_JS", "FAV_JS", "VISIT_JS"}
    def scripts(directory):
        result = {}
        for node in ast.parse((directory / 'tools/reads-theme/rebuild_index.py').read_text()).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in script_names:
                        result[target.id] = ast.dump(node.value, include_attributes=False)
        return result
    original_scripts, current_scripts = scripts(baseline), scripts(staged)
    scripts_unchanged = (set(original_scripts) == script_names
                         and original_scripts == current_scripts)
    def reading_behavior(directory):
        for node in ast.parse((directory / 'tools/reads-theme/rebuild_index.py').read_text()).body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "POST_CHROME_JS"
                for target in node.targets
            ):
                script = ast.literal_eval(node.value)
                anchor = "  var rt=document.getElementById('read-time');"
                assert anchor in script, "Missing article reading controls"
                return script.split(anchor, 1)[1]
        raise AssertionError("Missing article reading script")
    scripts_unchanged = scripts_unchanged and reading_behavior(baseline) == reading_behavior(staged)
    if not scripts_unchanged:
        errors.append("Non-theme search/preferences/favorites/visits/reading behavior changed")
    if (staged / "assets/reads-theme.js").read_bytes() != (staged / "tools/reads-theme/reads_theme.js").read_bytes():
        errors.append("Published color-mode script does not match its source")
    return {
        "article_count": dict(counts),
        "styled_articles": sum(counts.values()) - len(empty),
        "empty_sources_preserved": empty,
        "legacy_fragments_wrapped": fragments,
        "search_data_unchanged": search_unchanged,
        "non_theme_interactions_unchanged": scripts_unchanged,
        "stylesheet_matches_source": stylesheet_matches_source,
        "errors": errors,
        "passed": not errors,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("staged", type=Path)
    args = parser.parse_args()
    result = verify(args.baseline, args.staged)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
