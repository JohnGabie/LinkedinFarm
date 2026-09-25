# config/web_scraper_profiles.py

import json
import os
import re
from datetime import datetime

from config.button_handler import CONNECT_LINK_SELECTOR

# O cartão de resultado não tem mais atributo próprio (o antigo era
# div[data-chameleon-result-urn]) nem classe estável. Achamos ele subindo do
# link "Conectar" até o primeiro ancestral que contém o link do perfil.
CARD_FROM_CONNECT_XPATH = "xpath=ancestor::div[.//a[contains(@href,'/in/')]][1]"
PROFILE_LINK_IN_CARD = "a[href*='/in/']"
# Dentro do cartão, cargo e cidade são os únicos <span> sem atributo nenhum,
# nessa ordem (o terceiro é o texto "Conectar").
PLAIN_SPANS_IN_CARD = "span:not([class])"


def scrape_profiles(page):
    profiles_data = []
    try:
        # Os cartões entram por JS bem depois do domcontentloaded. Esperar aqui
        # dentro, e não no chamador, porque é esta função que depende deles —
        # e não dá pra esperar por a[href*='/in/'], que já casa com a navegação
        # do topo e retorna imediatamente com a lista ainda vazia.
        try:
            page.wait_for_selector(CONNECT_LINK_SELECTOR, timeout=10000)
        except Exception:
            pass  # página sem ninguém pra conectar é resultado válido, não erro

        links = page.locator(CONNECT_LINK_SELECTOR)
        total = links.count()
        if not total:
            print("[ℹ️] Nenhum link de conectar visível para scraping.")
            return []

        for i in range(total):
            try:
                link = links.nth(i)
                card = link.locator(CARD_FROM_CONNECT_XPATH).first

                profile = card.locator(PROFILE_LINK_IN_CARD).first
                name = profile.inner_text().strip() if profile.count() else "N/A"
                profile_url = (profile.get_attribute("href") or "").split("?")[0]

                spans = card.locator(PLAIN_SPANS_IN_CARD)
                texts = [spans.nth(j).inner_text().strip() for j in range(spans.count())]
                role = texts[0] if len(texts) > 0 else "N/A"
                city = texts[1] if len(texts) > 1 else "N/A"

                # o href do convite carrega o slug do perfil de graça
                vanity = re.search(r"vanityName=([^&]+)", link.get_attribute("href") or "")

                profiles_data.append({
                    "name": name,
                    "role": role,
                    "city": city,
                    "profile_url": profile_url,
                    "vanity_name": vanity.group(1) if vanity else None,
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
