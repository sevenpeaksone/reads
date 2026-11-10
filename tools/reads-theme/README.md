# 7Peaks Reads design — lime-v2

English canonical guide. Korean translation: [README.ko.md](README.ko.md).

This is the approved design source for the existing [Reads site](https://sevenpeaksone.github.io/reads/). Keep GitHub Pages hosting, existing article URLs, the archive, categories, search data, favorites, and the daily publishing contract. Do not migrate article files to Cloudflare Pages or R2.

## Design source

- `reads_theme.css`: the complete canonical layout and design, not an override of a separate dark stylesheet. Ivory `#F6F8ED`, charcoal `#17201B`, lime `#D5F43B`, orange `#F28B3C`, purple `#9270D8`, green `#2BA978`.
- `assets/7peaks-wordmark-light.svg`: approved wordmark. Do not redraw it or prepend another 7.
- `reads_article_template.html`: standalone article structure.
- `render_reads_article.py`: deterministic assembly with the template, stylesheet, and inline wordmark.
- `rebuild_index.py`: common listing/article generator. It installs the public logo and `assets/reads-theme.css` into the site.
- `test_reads_theme.py`: standalone/new-article publishing tests.
- `verify_reads_theme.py`: read-only comparison of original/restyled article bodies, image references, links, and search records.

In Reads these files live in `tools/reads-theme/`. In the producer project the same resources live in `docs/`, with this guide named `docs/READS_DESIGN.md` and its Korean companion `docs/READS_DESIGN.ko.md`.

## Source and generated HTML

Published listing pages and every non-empty article reference the same repository-local `assets/reads-theme.css?v=lime-v2`. The generator copies that stylesheet from this source directory. Old listing/chrome styles are no longer embedded ahead of the new design. Original article-specific markup and styles remain intact for content compatibility; the common theme normalizes their presentation. Standalone article previews embed this exact same stylesheet. A theme change must update this source, regenerate the site, and update the producer copy so future articles retain the design.

## Future article assembly

Do not invent CSS for each article. Render the existing draft Markdown into a body HTML fragment using the existing workflow. Exclude document tags and the first article-title h1; pass its title separately. Preserve prose, source links, dates, and `./images/...` paths.

In the producer project:

```sh
python3 docs/render_reads_article.py \
  --title "Article title" --category "IT" --date "2026-11-10" \
  --body output/topic/body.html --output output/topic/final.html
```

Use actual metadata, not the example values. Existing output is not overwritten by default; inspect and back it up before adding `--overwrite` when needed. The helper escapes metadata and embeds the exact stylesheet/wordmark, so local preview needs no remote stylesheet. Keep `final.md` for content review.

The final document has one h1, `body[data-reads-view="article"]`, and `data-reads-theme="lime-v2"`. Leave no unresolved template tokens. Hashtags belong in a paragraph, not another h1. Keep image content/relative paths, meaningful alt text, and responsive sizing. Styling must not change research, editorial rules, image generation, or subjects. Do not add unimplemented AI/wiki features to company marketing; this does not prohibit news about AI.

## Publishing contract

Keep the existing outbox/READY workflow and schedule. Producer `site.tgz` archives contain **only `posts/` or `news/` article folders and images**; do not add root `assets/` or `tools/` paths. The receiver's generator installs common assets, replaces preview-only CSS/navigation with one common site chrome, and applies the approved design even when an incoming article has older inline styles.

Verify every planned article and referenced file before writing READY last. Do not emit empty articles or mark partial batches complete. Do not directly push Git, change credentials/schedules/history files, or modify the publishing script as a styling workaround. Report missing historical content/images separately; do not invent, delete, or silently repair them.

## Checks

From the Reads repository root:

```sh
python3 -B -m unittest discover -s tools/reads-theme -p 'test_reads_theme.py' -v
```

Run bulk generation on an internal-disk copy with `SITE` set to that explicit site directory, never on the external SSD. Check one news/blog article at desktop/mobile widths, image references, search, favorites, pagination, and article light/dark mode. Report preview, source installation, commit/push, and verified live deployment as separate states.
