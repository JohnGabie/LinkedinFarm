from playwright.sync_api import Page

LIMIT_MODAL_SELECTOR   = "div.artdeco-modal.ip-fuse-limit-alert[role='dialog']"
LIMIT_HEADER_SELECTOR  = "h2.ip-fuse-limit-alert__header"
LIMIT_OK_BUTTON        = "button.ip-fuse-limit-alert__primary-action"

def get_connect_buttons(page: Page):
    try:
        page.wait_for_selector("button:has-text('Conectar')", timeout=1000)
        return page.query_selector_all("button:has-text('Conectar')")
    except Exception as e:
        print(f"[Nenhum botão 'Conectar' encontrado]")
        return []

def process_connect_button(button, page: Page):
    try:
        button.click()
        page.wait_for_selector("button:has-text('Enviar sem nota')", timeout=2000)
        send_btn = page.query_selector("button:has-text('Enviar sem nota')")
        if send_btn:
            send_btn.click()
            return True  # conexão feita
    except Exception as e:
        print(f"[Erro ao clicar ou enviar conexão] {e}")
    return False  # falhou ou já conectado

def go_to_next_page(page: Page):
    try:
        # 1. Tentar encontrar botão "Avançar" por texto (padrão LinkedIn)
        next_button = page.query_selector("button:has-text('Avançar'), a:has-text('Avançar')")

        # 2. Se não achar, tenta pegar qualquer link com "page=" + 2, 3...
        if not next_button:
            next_button = page.query_selector("a[aria-label*='Próxima'], a[aria-label*='Avançar']")

        if next_button:
            # Scroll até o botão, se necessário
            next_button.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            next_button.click()
            page.wait_for_timeout(3000)
            return True
        else:
            print("[❌] Botão de próxima página não encontrado.")
    except Exception as e:
        print(f"[❌] Erro ao clicar no botão de próxima página: {e}")
    return False

def close_popup_if_present(page: Page):
    try:
        popup = page.query_selector('xpath=//*[@id="ember1071"]')
        if popup:
            popup.scroll_into_view_if_needed()
            popup.click()
            page.wait_for_timeout(1000)
            print("[✔] Pop-up fechado com sucesso.")
    except Exception as e:
        print(f"[❌] Erro ao tentar fechar pop-up: {e}")

def hit_weekly_limit(page) -> bool:
    try:
        # Checa o modal direto
        modal = page.query_selector(LIMIT_MODAL_SELECTOR)
        if modal and modal.is_visible():
            return True

        # Fallback: checa o header (caso o modal ainda esteja montando)
        header = page.query_selector(LIMIT_HEADER_SELECTOR)
        if header:
            txt = (header.inner_text() or "").strip().lower()
            if "limite semanal" in txt or "limite semanal de convites" in txt:
                return True
    except Exception:
        pass
    return False