from core.orchestrator import BrowserOrchestrator
from config.button_handler import get_connect_buttons, process_connect_button, hit_weekly_limit
from config.linkedin_search import LinkedInSearch
from config.web_scraper_profiles import scrape_profiles, save_to_bank, load_connection_count

MAX_CONNECTIONS = 200

def main():
    # Inicia o orchestrator (já cuida do login via Core)
    orch = BrowserOrchestrator.instance()
    page = orch.open_page()

    try:
        # ==== LÓGICA ANTIGA MANTIDA ====
        print("Login attempt: Success")

        search = LinkedInSearch("Dell", "1")
        search_url = search.get_url()
        print(f"Navigating to search URL: {search_url}")

        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")

        title = page.title()
        print(f"Page title: {title}")

        print("Executando Bot de conexão inicial...")
        scraped_profiles = scrape_profiles(page)
        save_to_bank(scraped_profiles)

        connections_made = load_connection_count() or 0

        for page_num in range(1, 101):  # Itera até 100 páginas
            search.set_page(page_num)
            url = search.get_url()
            page.goto(url)

            try:
                page.wait_for_selector("div[data-chameleon-result-urn]")
            except Exception:
                print(f"[!] Nenhum conteúdo de perfil carregado na página {page_num}. Encerrando busca.")
                break

            connect_buttons = get_connect_buttons(page)

            if connect_buttons:
                conexoes_feitas_na_pagina = 0
                for button in connect_buttons:
                    process_connect_button(button, page)
                    conexoes_feitas_na_pagina += 1
                    connections_made += 1
                    if connections_made >= MAX_CONNECTIONS:
                        break
                print(f"[✔] Página {page_num}: {conexoes_feitas_na_pagina} conexões feitas de total({connections_made}).")
            else:
                print(f"[→] Página {page_num}: 0 conexões encontradas de total({connections_made}).")

            if connections_made >= MAX_CONNECTIONS:
                print(f"[✔] Limite de {MAX_CONNECTIONS} conexões atingido. Encerrando o processo.")
                break

            page.wait_for_timeout(500)

            if hit_weekly_limit(page):
                print("[!] Limite semanal já ativo nesta página. Encerrando.")
                orch.close_page(page)
                return

    finally:
        orch.close_page(page)

if __name__ == "__main__":
    main()
