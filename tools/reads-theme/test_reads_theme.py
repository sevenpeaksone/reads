"""Tests for standalone assembly and the unchanged daily-publisher interface."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from render_reads_article import render_article, THEME_DIR


class ReadsThemeTests(unittest.TestCase):
    def test_escaped_metadata_and_unchanged_body(self):
        body = '<p>Original text {{TITLE_ESCAPED}}</p><img src="./images/thumbnail.png" alt="Example">'
        result = render_article('Title <one> & two', 'IT & science', '2026-11-10', body)
        self.assertIn('Title &lt;one&gt; &amp; two', result)
        self.assertIn('IT &amp; science', result)
        self.assertIn(body, result)
        self.assertIn('data-reads-theme="lime-v4"', result)
        self.assertIn('class="reads-wordmark"', result)
        self.assertEqual(result.count('<h1>'), 1)
        self.assertEqual(result.count('id="reads-theme-init"'), 1)
        self.assertEqual(result.count('id="reads-theme-script"'), 1)
        self.assertEqual(result.count('id="theme-toggle"'), 1)

    def test_rejects_empty_content(self):
        with self.assertRaises(ValueError):
            render_article('Title', 'News', '2026-11-10', ' ')

    def test_rejects_invalid_date(self):
        with self.assertRaises(ValueError):
            render_article('Title', 'News', '2026-99-99', '<p>Body</p>')

    def test_rejects_nested_document(self):
        with self.assertRaises(ValueError):
            render_article('Title', 'News', '2026-11-10', '<body>Body</body>')

    def test_rejects_duplicate_heading(self):
        with self.assertRaises(ValueError):
            render_article('Title', 'News', '2026-11-10', '<h1>Duplicate title</h1>')

    def test_publish_and_republish_blog_and_news(self):
        with tempfile.TemporaryDirectory(prefix='reads-theme-test-') as directory:
            site = Path(directory)
            articles = [
                ('posts/it/2026-11-10-03', 'Test blog', 'IT'),
                ('news/economy/2026-11-10-20', 'Test news', '경제'),
            ]
            body = '<p>Preserved article body.</p><h2>Details</h2><p>More text.</p>'
            for path, title, category in articles:
                target = site / path / 'index.html'
                target.parent.mkdir(parents=True)
                target.write_text(render_article(title, category, '2026-11-10', body), encoding='utf-8')
            env = dict(os.environ, SITE=str(site), GOATCOUNTER_CODE='')
            previous = {}
            for _ in range(2):
                subprocess.run([sys.executable, '-B', str(THEME_DIR / 'rebuild_index.py')],
                               env=env, check=True, capture_output=True, text=True)
                for path, title, category in articles:
                    result = (site / path / 'index.html').read_text(encoding='utf-8')
                    self.assertIn(body, result)
                    self.assertEqual(result.count('id="site-nav"'), 1)
                    self.assertEqual(result.count('id="site-chrome-css"'), 1)
                    self.assertEqual(result.count('id="site-chrome-js"'), 1)
                    self.assertNotIn('id="reads-article-theme"', result)
                    self.assertIn('data-reads-theme="lime-v4"', result)
                    self.assertIn('href="/reads/assets/reads-theme.css?v=lime-v4"', result)
                    self.assertNotIn('<style id="site-chrome-css"', result)
                    for marker in ('id="reads-theme-init"', 'id="reads-theme-script"', 'id="theme-toggle"'):
                        self.assertEqual(result.count(marker), 1)
                    self.assertIn('/reads/assets/reads-theme.js?v=lime-v4', result)
                    if path in previous:
                        self.assertEqual(previous[path], result)
                    previous[path] = result
            for relative in ('index.html', 'posts/index.html', 'news/index.html', 'favorites.html'):
                result = (site / relative).read_text(encoding='utf-8')
                self.assertIn('id="reads-theme"', result)
                self.assertIn('href="/reads/assets/reads-theme.css?v=lime-v4"', result)
                self.assertNotIn('--bg:#0f1117', result)
                self.assertEqual(result.count('id="theme-toggle"'), 1)
                self.assertIn('class="reads-controls"', result)
                self.assertLess(result.index('id="reads-theme-init"'), result.index('id="reads-theme"'))
                self.assertIn('/reads/assets/reads-theme.js?v=lime-v4', result)
            self.assertEqual(len(json.loads((site / 'search.json').read_text())), 2)
            self.assertEqual((site / 'assets/reads-theme.css').read_bytes(),
                             (THEME_DIR / 'reads_theme.css').read_bytes())
            self.assertEqual((site / 'assets/reads-theme.js').read_bytes(),
                             (THEME_DIR / 'reads_theme.js').read_bytes())
            self.assertTrue((site / 'assets/7peaks-wordmark-light.svg').is_file())
            self.assertEqual((site / 'assets/7peaks-point-field.png').read_bytes(),
                             (THEME_DIR / 'assets/7peaks-point-field.png').read_bytes())
            home = (site / 'index.html').read_text(encoding='utf-8')
            self.assertIn('hero hero-split', home)
            self.assertIn('오늘을 읽고,<br>생각을 넓히다.', home)
            self.assertIn('href="#reading"', home)
            self.assertIn('<main id="reading">', home)
            css = (THEME_DIR / 'reads_theme.css').read_text(encoding='utf-8')
            self.assertIn('Geist Variable', css)
            self.assertIn('Noto Sans KR Variable', css)
            self.assertIn('prefers-reduced-motion', css)


    def test_legacy_article_is_upgraded_without_changing_content(self):
        with tempfile.TemporaryDirectory(prefix='reads-legacy-theme-test-') as directory:
            site = Path(directory)
            target = site / 'posts/it/2026-11-10-03/index.html'
            target.parent.mkdir(parents=True)
            body = '<main><h1>Existing article</h1><p>Original words.</p><img src="./images/original.png"></main>'
            target.write_text(
                '<!DOCTYPE html><html lang="ko" data-reads-theme="lime-v1">'
                '<head><title>Existing article</title><style id="site-chrome-css">body{background:black}</style></head>'
                '<body data-reads-view="article" data-reads-theme="lime-v1">' + body + '</body></html>',
                encoding='utf-8')
            env = dict(os.environ, SITE=str(site), GOATCOUNTER_CODE='')
            for _ in range(2):
                subprocess.run([sys.executable, '-B', str(THEME_DIR / 'rebuild_index.py')],
                               env=env, check=True, capture_output=True, text=True)
                result = target.read_text(encoding='utf-8')
                self.assertIn(body, result)
                self.assertNotIn('data-reads-theme="lime-v1"', result)
                self.assertEqual(result.count('id="site-chrome-css"'), 1)
                self.assertIn('<link id="site-chrome-css"', result)
                self.assertNotIn('body{background:black}', result)


if __name__ == '__main__':
    unittest.main()
