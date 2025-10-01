# config/web_scraper_profiles.py

import json
import os
from datetime import datetime


def scrape_profiles(page):
    profiles_data = []
    try:
        # NÃO usar wait_for_selector aqui
        buttons = page.query_selector_all("button:has-text('Conectar')")
        if not buttons:
            print("[ℹ️] Nenhum botão de conectar visível para scraping.")
            return []

        for button in buttons:
            try:
                profile_container = button.evaluate_handle("el => el.closest('div[data-chameleon-result-urn]')")
                if not profile_container:
                    continue

                name_el = profile_container.query_selector("span[dir='ltr']")
                role_el = profile_container.query_selector("div.t-14.t-black.t-normal")
                city_el = profile_container.query_selector("div.t-14.t-normal >> nth=1")

                name = name_el.inner_text().strip() if name_el else "N/A"
                role = role_el.inner_text().strip() if role_el else "N/A"
                city = city_el.inner_text().strip() if city_el else "N/A"

                profiles_data.append({
                    "name": name,
                    "role": role,
                    "city": city,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                print(f"Erro ao extrair um perfil: {e}")
                continue

    except Exception as e:
        print(f"Erro geral ao extrair perfis: {e}")
    return profiles_data


def save_connection_count(count, path="connections.json"):
    with open(path, "w") as f:
        json.dump({"connections_made": count}, f)

def load_connection_count(path="connections.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("connections_made", 0)
    return 0

def save_to_bank(data, path="profiles.json"):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[✔] {len(data)} perfis salvos em {path}")
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
