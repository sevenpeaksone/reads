# 7Peaks Reads design — light-v8

English canonical guide. Korean translation: [README.ko.md](README.ko.md).

This is the approved design source for the existing [Reads site](https://sevenpeaksone.github.io/reads/). Keep GitHub Pages hosting, existing article URLs, the archive, categories, search data, favorites, and the daily publishing contract. Do not migrate article files to Cloudflare Pages or R2.

## Design source

- `reads_theme.css`: the complete canonical layout and design, not an override of a separate dark stylesheet. Ivory `#F6F8ED`, charcoal `#17201B`, lime `#D5F43B`, orange `#F28B3C`, purple `#9270D8`, green `#2BA978`.
- `reads_theme_init.js` / `reads_theme.js`: pre-paint light-only initialization and cleanup of retired theme controls/preferences.
- `assets/7peaks-a-lockup.webp`: approved A symbol and light-weight wordmark. Do not redraw it or prepend another 7.
- `reads_article_template.html`: standalone article structure.
- `render_reads_article.py`: deterministic assembly with the template, stylesheet, and inline wordmark.
- `rebuild_index.py`: common listing/article generator. It installs the public logo and `assets/reads-theme.css` into the site.
- `test_reads_theme.py`: standalone/new-article publishing tests.
- `verify_reads_theme.py`: read-only comparison of original/restyled article bodies, image references, links, and search records.

In Reads these files live in `tools/reads-theme/`. In the producer project the same resources live in `docs/`, with this guide named `docs/READS_DESIGN.md` and its Korean companion `docs/READS_DESIGN.ko.md`.

## Company identity alignment

Reads is a distinct service for reading stories about the world, not a copy of the company landing page. It shares the A symbol, original wordmark at a reduced display height, typefaces, ivory/charcoal/lime tokens and 32px visually slim controls. Its compact masthead leads directly into news and blog articles. The company home photographs, slides and marketing hero must never be inserted into Reads. Selected B imagery remains on the Reads home route only, softly feathered into the ivory surface. Blog and news landing pages are text-only: retain their titles, descriptions and reading links, omit the editorial figure, and remove the reserved image column and minimum height. Do not reinsert decorative book/newspaper images when rebuilding. The original logo is proportionally displayed at exactly one-third of the original company header at commit 433f751 (image-canvas heights approximately 31.78px, 26px and 23.11px at the original 1100px/600px breakpoints), not one-third of a reduced intermediate preview; navigation text is unchanged, while content headings/body are smaller. Orange, purple and green remain editorial category accents. Preserve search, favorites, view preferences, pagination, reading progress, and all article content.

The two pinned Fontsource 5.3.0 font stylesheets load through jsDelivr. Layout remains local; offline previews fall back to system fonts. Company photo assets are not used on Reads. The home reading image is assets/reads-world-b.webp; assets/reads-news-paper.webp is retained as an inactive source asset, not displayed on the news landing page. Do not recolor, resize, recompress, replace, or delete article images. Archive point-field and old-logo assets are not active design sources.

## Source and generated HTML

Published listings and every non-empty article reference `assets/reads-theme.css?v=light-v8` and the matching shared script. Original article-specific markup remains intact; the common theme normalizes presentation. Standalone previews embed the exact stylesheet and logo image. Update this source, regenerate the site, and synchronize the producer copy so future articles retain the same design.

## Light-only presentation

The owner removed dark mode on 2026-11-17. Home, listings, archives, favorites and articles must always use the light identity, even when the OS or a retired saved preference is dark. Do not emit theme-toggle markup or dark-mode CSS. Apply light mode in the document head before styles, remove only the retired `spk-theme` key, and handle stale back/forward pages or tabs. Do not remove favorites, search/view preferences, or other storage. Blocked storage must not prevent light rendering. New standalone articles use the same light-only initializer.

## Future article assembly

Do not invent CSS for each article. Render the existing draft Markdown into a body HTML fragment using the existing workflow. Exclude document tags and the first article-title h1; pass its title separately. Preserve prose, source links, dates, and `./images/...` paths.

In the producer project:

```sh
python3 docs/render_reads_article.py \
  --title "Article title" --category "IT" --date "2026-11-10" \
  --body output/topic/body.html --output output/topic/final.html
```

Use actual metadata, not the example values. Existing output is not overwritten by default; inspect and back it up before adding `--overwrite` when needed. The helper escapes metadata and embeds the exact stylesheet/wordmark, so local preview needs no remote stylesheet. Keep `final.md` for content review.

The final document has one h1, `body[data-reads-view="article"]`, and `data-reads-theme="light-v8"`. Leave no unresolved template tokens. Hashtags belong in a paragraph, not another h1. Keep image content/relative paths, meaningful alt text, and responsive sizing. Styling must not change research, editorial rules, image generation, or subjects. Do not add unimplemented AI/wiki features to company marketing; this does not prohibit news about AI.

## Publishing contract

Keep the existing outbox/READY workflow and schedule. Producer `site.tgz` archives contain **only `posts/` or `news/` article folders and images**; do not add root `assets/` or `tools/` paths. The receiver's generator installs common assets, replaces preview-only CSS/navigation with one common site chrome, and applies the approved design even when an incoming article has older inline styles.

Verify every planned article and referenced file before writing READY last. Do not emit empty articles or mark partial batches complete. Do not directly push Git, change credentials/schedules/history files, or modify the publishing script as a styling workaround. Report missing historical content/images separately; do not invent, delete, or silently repair them.

## Checks

From the Reads repository root:

```sh
python3 -B -m unittest discover -s tools/reads-theme -p 'test_reads_theme.py' -v
node --test tools/reads-theme/test_reads_theme_script.mjs
```

Run bulk generation on an internal-disk copy with `SITE` set to that explicit directory, never on the external SSD. Check news/blog articles at desktop/mobile widths, image references, search, favorites, pagination, and light rendering with old saved dark preferences. Report preview, source installation, commit/push, and verified live deployment separately.
