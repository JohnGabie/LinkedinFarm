from playwright.sync_api import Page

# ---------------------------------------------------------------------------
# Seletores da busca de pessoas. Mapeados contra a página real em 2026-09-24.
#
# O LinkedIn migrou essa tela pra Server-Driven UI: as classes viraram hashes
# que rodam a cada deploy (_9cd37f2c, e078840b...) e o antigo
# div[data-chameleon-result-urn] não existe mais. Nada aqui pode depender de
# classe. O que sobrou de estável:
#   - href semântico (/search-custom-invite/) para o "Conectar"
#   - href /in/ para o perfil
#   - o modal de convite, que ainda é o artdeco antigo com role=dialog
# ---------------------------------------------------------------------------

# "Conectar" virou <a>, não <button>. O href também entrega o vanityName.
CONNECT_LINK_SELECTOR = "a[href*='/search-custom-invite/']"
# Link do perfil dentro do cartão.
# NÃO serve de âncora de "carregou": casa com a navegação do topo e já retorna
# 80 matches no domcontentloaded, com a lista de resultados ainda vazia.
PROFILE_LINK_SELECTOR = "a[href*='/in/']"
# Container da lista de resultados — este sim indica que a lista renderizou.
RESULTS_LIST_SELECTOR = "[data-testid='lazy-column']"
# Modal "Adicionar nota ao seu convite?" — este sobreviveu à migração.
SEND_WITHOUT_NOTE_SELECTOR = "button:has-text('Enviar sem nota')"
INVITE_DIALOG_SELECTOR = "[role=dialog]"
NEXT_PAGE_SELECTOR = "button:has-text('Próxima')"

LIMIT_TEXTS = ("limite semanal", "weekly invitation limit", "atingiu o limite")

# Pausa entre convites. Não é enfeite: sem ela o loop clica encostado e o modal
# de confirmação não acompanha — medido em ~50% de falha sem pausa contra 0%
# com 1,5s. De quebra, é o que faz o ritmo parecer humano.
DELAY_BETWEEN_INVITES_MS = 1500


def get_connect_buttons(page: Page):
    """Links 'Conectar' da página atual.

    Ancora cada um pelo próprio href (único por perfil) em vez de por índice:
    clicar num convite re-renderiza a lista, e um locator por posição passaria
    a apontar pro cartão errado no meio do loop.
    """
    try:
        page.wait_for_selector(CONNECT_LINK_SELECTOR, timeout=5000)
    except Exception:
        print("[Nenhum link 'Conectar' encontrado]")
        return []

    links = page.locator(CONNECT_LINK_SELECTOR)
    hrefs = []
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        if href and href not in hrefs:
            hrefs.append(href)
    return [page.locator(f'a[href="{href}"]').first for href in hrefs]


def process_connect_button(button, page: Page):
    """Clica em 'Conectar' e confirma com 'Enviar sem nota'.

    O clique só abre o modal; o convite sai mesmo no 'Enviar sem nota'.
    """
    try:
        button.scroll_into_view_if_needed(timeout=5000)
        button.click(timeout=5000)
        page.wait_for_selector(SEND_WITHOUT_NOTE_SELECTOR, timeout=5000)
        page.locator(SEND_WITHOUT_NOTE_SELECTOR).first.click()
        # espera o modal sumir: é o que confirma que o convite foi aceito
        page.wait_for_selector(INVITE_DIALOG_SELECTOR, state="detached", timeout=5000)
        return True
    except Exception as e:
        print(f"[Erro ao clicar ou enviar conexão] {e}")
        # deixa a tela limpa pro próximo perfil, senão o modal aberto
        # intercepta todos os cliques seguintes
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
        except Exception:
            pass
        return False
    finally:
        page.wait_for_timeout(DELAY_BETWEEN_INVITES_MS)


def go_to_next_page(page: Page):
    """Avança a paginação pelo botão.

    Obs: o fluxo principal do bot navega por URL (search.set_page), então isso
    aqui é alternativa, não caminho padrão.
    """
    try:
        next_button = page.locator(NEXT_PAGE_SELECTOR).first
        if next_button.count() and next_button.is_visible():
            next_button.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            next_button.click()
            page.wait_for_timeout(3000)
            return True
        print("[❌] Botão de próxima página não encontrado.")
    except Exception as e:
        print(f"[❌] Erro ao clicar no botão de próxima página: {e}")
    return False


def close_popup_if_present(page: Page):
    """Fecha qualquer modal aberto. Escape resolve os do LinkedIn."""
    try:
        if page.locator(INVITE_DIALOG_SELECTOR).count():
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
            print("[✔] Pop-up fechado com sucesso.")
    except Exception as e:
        print(f"[❌] Erro ao tentar fechar pop-up: {e}")


def hit_weekly_limit(page) -> bool:
    """Detecta o aviso de limite semanal de convites.

    Por texto, não por classe: o antigo .ip-fuse-limit-alert é do design system
    velho. Não deu pra testar ao vivo — só aparece quando o limite estoura.
    """
    try:
        dialogs = page.locator(INVITE_DIALOG_SELECTOR)
        for i in range(dialogs.count()):
            if not dialogs.nth(i).is_visible():
                continue
            text = (dialogs.nth(i).inner_text() or "").strip().lower()
            if any(marker in text for marker in LIMIT_TEXTS):
                return True
    except Exception:
        pass
    return False
