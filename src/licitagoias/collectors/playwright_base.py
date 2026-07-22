from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, sync_playwright


class PlaywrightSession:
    def __init__(self, headless: bool = True, storage_dir: Path | None = None) -> None:
        self.headless = headless
        self.storage_dir = storage_dir or Path("data/raw/html")

    def run(self, url: str, handler) -> list[dict]:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                self._save_snapshot(page, url)
                return handler(page)
            finally:
                browser.close()

    def _save_snapshot(self, page: Page, url: str) -> None:
        safe_name = "".join(char if char.isalnum() else "_" for char in url)[:120]
        (self.storage_dir / f"{safe_name}.html").write_text(page.content(), encoding="utf-8")
