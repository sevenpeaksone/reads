# 7Peaks Reads

News, commentary, and blog articles published at [7Peaks Reads](https://sevenpeaksone.github.io/reads/).

Korean: [README.ko.md](README.ko.md).

The website and articles use the **light-v5** design: ivory, charcoal, lime, orange, purple, and green. The main page, news, blog, category archives, favorites, and existing articles use the same common design.

Reads follows the company website's light identity: the approved A-symbol wordmark, thin Geist/Noto Sans KR typography, generous layout, lime navigation, compact charcoal controls, and a home photograph that blends into the background. Reading screens adapt that system to articles rather than introducing a separate magazine theme.

The site is light-only, including the home page, all listings, favorites, and article details. Dark-mode controls are removed. Old saved dark preferences are retired without changing favorites or view preferences.

- Published design: [`assets/reads-theme.css`](assets/reads-theme.css).
- Editable design source: [`tools/reads-theme/reads_theme.css`](tools/reads-theme/reads_theme.css).
- Generator, standalone article template, and checks: [design guide](tools/reads-theme/README.md).

Update the source and regenerate HTML rather than adding another legacy CSS layer. Keep the producer's matching template and stylesheet in sync so future articles retain the design. Read the design guide before creating or changing article HTML.

Keep existing article paths, images, categories, archive, search IDs, favorites, and the current publishing workflow. This repository continues using GitHub Pages; article files are not moved to Cloudflare.
