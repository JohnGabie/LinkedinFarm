from playwright.sync_api import sync_playwright
from core.handle.try_login import try_login
import os
import time

class SessionManager:
    def __init__(self, user_data_dir=None, headless=False, manual_login_timeout=300):
        if user_data_dir is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            user_data_dir = os.path.join(BASE_DIR, "core", ".user_data")
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.manual_login_timeout = manual_login_timeout
        self._playwright = None
        self._ctx = None

    def start(self):
        if self._ctx:
            return self._ctx

        self._playwright = sync_playwright().start()
        self._ctx = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
        )

        # garante login
        page = self._ctx.new_page()
        try:
            page.goto("https://www.linkedin.com/feed/", timeout=60_000)
            if "login" in page.url:
                if not try_login(page) and not self.headless:
                    # Sem credenciais, ou o LinkedIn pediu captcha/verificação:
                    # a sessão fica salva no user_data_dir, então basta uma vez.
                    self.wait_for_manual_login(page)
        finally:
            page.close()

        return self._ctx

    def wait_for_manual_login(self, page):
        """Espera o usuário logar na janela do navegador que já está aberta."""
        print(f"\n[!] Faça o login na janela do Chromium que abriu.")
        print(f"    Aguardando até {self.manual_login_timeout}s...\n")
        deadline = time.time() + self.manual_login_timeout
        while time.time() < deadline:
            url = page.url
            if "login" not in url and "checkpoint" not in url and "authwall" not in url:
                print("[OK] Sessão autenticada — salva em", self.user_data_dir)
                return True
            page.wait_for_timeout(2000)
        print("[X] Tempo esgotado sem login.")
        return False

    def stop(self):
        if self._ctx:
            self._ctx.close()
            self._playwright.stop()
            self._ctx = None
