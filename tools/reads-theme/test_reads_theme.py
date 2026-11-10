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
        self.assertIn('data-reads-theme="lime-v1"', result)
        self.assertIn('class="reads-wordmark"', result)
        self.assertEqual(result.count('<h1>'), 1)

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
                    self.assertIn('data-reads-theme="lime-v1"', result)
            self.assertEqual(len(json.loads((site / 'search.json').read_text())), 2)
            self.assertEqual((site / 'assets/reads-theme.css').read_bytes(),
                             (THEME_DIR / 'reads_theme.css').read_bytes())
            self.assertTrue((site / 'assets/7peaks-wordmark-light.svg').is_file())


if __name__ == '__main__':
    unittest.main()
