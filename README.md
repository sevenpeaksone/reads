# 7Peaks Reads

News, commentary, and blog articles published at [7Peaks Reads](https://sevenpeaksone.github.io/reads/).

Korean: [README.ko.md](README.ko.md).

The website and articles use the **lime-v4** design: ivory, charcoal, lime, orange, purple, and green. The main page, news, blog, category archives, favorites, and existing articles use the same common design.

Reads now follows the company website's Light identity: the same wordmark, Geist/Noto Sans KR typography, generous layout, lime underline navigation, charcoal controls, and approved point-field artwork. Reading screens adapt that system to articles rather than introducing a separate magazine theme.

Light/dark mode is shared by the home page, all listings, favorites, and article details. The header toggle preserves one choice across navigation and reloads; new visitors default to light.

- Published design: [`assets/reads-theme.css`](assets/reads-theme.css).
- Editable design source: [`tools/reads-theme/reads_theme.css`](tools/reads-theme/reads_theme.css).
- Generator, standalone article template, and checks: [design guide](tools/reads-theme/README.md).

Update the source and regenerate HTML rather than adding another legacy CSS layer. Keep the producer's matching template and stylesheet in sync so future articles retain the design. Read the design guide before creating or changing article HTML.

Keep existing article paths, images, categories, archive, search IDs, favorites, and the current publishing workflow. This repository continues using GitHub Pages; article files are not moved to Cloudflare.
