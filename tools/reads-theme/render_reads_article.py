"""Assemble a standalone Reads article using the versioned, approved design."""
import argparse
from datetime import date
import html
from pathlib import Path
import re


THEME_DIR = Path(__file__).resolve().parent


def render_article(title, category, published_date, body_html):
    date.fromisoformat(published_date)
    if not title.strip() or not category.strip() or not body_html.strip():
        raise ValueError("Title, category, and article body must be non-empty")
    if re.search(r"<(?:html|head|body|h1)\b", body_html, re.I):
        raise ValueError("Provide a body fragment without document tags or a duplicate h1")
    template = (THEME_DIR / "reads_article_template.html").read_text(encoding="utf-8")
    wordmark = (THEME_DIR / "assets/7peaks-wordmark-light.svg").read_text(encoding="utf-8")
    wordmark = wordmark.replace("<svg ", '<svg class="reads-wordmark" ', 1)
    values = {
        "TITLE_ESCAPED": html.escape(title),
        "CATEGORY_ESCAPED": html.escape(category),
        "DATE_ISO": published_date,
        "READS_THEME_CSS": (THEME_DIR / "reads_theme.css").read_text(encoding="utf-8"),
        "READS_WORDMARK_SVG": wordmark,
        "ARTICLE_BODY_HTML": body_html,
    }
    # Substitute once: article text that resembles a placeholder is editorial
    # content and must never be interpreted as template instructions.
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: values[match[1]], template)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--date", required=True, dest="published_date")
    parser.add_argument("--body", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = render_article(args.title, args.category, args.published_date,
                            args.body.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w" if args.overwrite else "x", encoding="utf-8") as target:
        target.write(output)
    print(args.output)
