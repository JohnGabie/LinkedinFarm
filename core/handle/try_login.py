import json
import os
import sys

from dotenv import load_dotenv


# Constantes
FEED_URL = "https://www.linkedin.com/feed/"
LOGIN_URL = "https://www.linkedin.com/login"
# O LinkedIn não usa mais <form>, nem name='session_key', nem button[type=submit]:
# os ids são ofuscados e trocam a cada carregamento. Só sobrou o type dos inputs.
# Atenção: a página renderiza um par de inputs INVISÍVEL antes do par real, por
# isso todo acesso passa por visible=true (ver first_visible).
SESSION_KEY_SELECTOR = "input[type='email']"
SESSION_PASSWORD_SELECTOR = "input[type='password']"
TIMEOUT = 10000  # 10 segundos
WAIT_AFTER_GOTO = 2000  # 2 segundos
WAIT_FOR_URL_TIMEOUT = 15000  # 15 segundos
DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_FILE = os.path.join(DIR, "core", "utils", "linkedin_credentials.json")

def first_visible(page, selector):
    """Primeiro elemento VISÍVEL do seletor, ou None.

    A página de login tem um par de inputs oculto antes do real; pegar o
    primeiro match cru preenche o campo errado.
    """
    loc = page.locator(selector)
    for i in range(loc.count()):
        if loc.nth(i).is_visible():
            return loc.nth(i)
    return None

def find_submit_button(page):
    """Acha o botão 'Entrar' sem depender de idioma nem de classe.

    Não existe mais button[type=submit]. O botão de entrar é o único botão
    visível SEM ícone abaixo do campo de senha — os de cima são os sociais
    (Microsoft/Apple/Google) e o olhinho de 'exibir senha', todos com <img>/<svg>.
    """
    password = first_visible(page, SESSION_PASSWORD_SELECTOR)
    if password is None:
        return None
    password_box = password.bounding_box()
    if password_box is None:
        return None

    buttons = page.locator("button")
    for i in range(buttons.count()):
        button = buttons.nth(i)
        if not button.is_visible():
            continue
        box = button.bounding_box()
        if box is None or box["y"] <= password_box["y"]:
            continue
        if button.locator("img, svg").count():
            continue
        return button
    return None

def load_credentials():
    """Carrega as credenciais do .env (ou variáveis de ambiente) e do JSON.

    O JSON guarda o token li_at em cache; email/senha do ambiente têm
    precedência sobre o que estiver salvo nele.
    """
    load_dotenv(os.path.join(DIR, ".env"))

    try:
        with open(JSON_FILE, "r") as f:
            credentials = json.load(f)
    except FileNotFoundError:
        credentials = {"platform": "linkedin", "login": "", "password": "", "auth": []}

    credentials["login"] = os.getenv("LINKEDIN_EMAIL") or credentials.get("login", "")
    credentials["password"] = os.getenv("LINKEDIN_PASSWORD") or credentials.get("password", "")

    # Sem credenciais, pergunta no terminal — mas nunca trava: sem terminal
    # (container, script, pipe) input() estoura EOFError e seguimos sem elas,
    # deixando o login manual assumir. Não dá pra confiar em stdin.isatty():
    # no Windows o NUL é char device e isatty() responde True.
    if not (credentials["login"] and credentials["password"]) and sys.stdin.isatty():
        print(f"Credenciais não encontradas em {JSON_FILE} nem em LINKEDIN_EMAIL/LINKEDIN_PASSWORD.")
        try:
            credentials["login"] = input("Email do LinkedIn (enter para pular): ").strip()
            credentials["password"] = input("Senha do LinkedIn (enter para pular): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("(sem terminal interativo — seguindo sem credenciais)")
            credentials["login"] = credentials["password"] = ""
        if credentials["login"] and credentials["password"]:
            save_credentials(credentials)

    return credentials

def save_credentials(data):
    """Salva as credenciais no arquivo JSON."""
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_auth_token(credentials):
    """Obtém o token de autenticação das credenciais, se existir e for válido."""
    auth_list = credentials.get("auth", [])
    return auth_list[0] if auth_list and auth_list[0].strip() else None

def are_credentials_valid(credentials):
    """Verifica se login e senha estão presentes."""
    return bool(credentials.get("login") and credentials.get("password"))

def attempt_token_login(context, page, token):
    """Tenta fazer login com um token de autenticação."""
    try:
        context.add_cookies([{"name": "li_at", "value": token, "domain": ".linkedin.com", "path": "/"}])
        page.goto(FEED_URL, timeout=TIMEOUT)
        page.wait_for_timeout(WAIT_AFTER_GOTO)
        if FEED_URL in page.url:
            print("Login bem-sucedido com token de autenticação.")
            return True
        else:
            print("Token de autenticação inválido.")
            return False
    except Exception as e:
        print(f"Falha no token de autenticação: {e}")
        return False

def attempt_credential_login(page, credentials):
    """Tenta fazer login com usuário e senha."""
    try:
        print("Tentando login com credenciais.")
        page.goto(LOGIN_URL, timeout=TIMEOUT)
        page.wait_for_selector(SESSION_KEY_SELECTOR, timeout=TIMEOUT, state="attached")

        email_field = first_visible(page, SESSION_KEY_SELECTOR)
        password_field = first_visible(page, SESSION_PASSWORD_SELECTOR)
        submit_button = find_submit_button(page)
        if not (email_field and password_field and submit_button):
            print("[!] Formulário de login não reconhecido — o LinkedIn mudou a página de novo.")
            page.screenshot(path="login_failure.png")
            return False

        email_field.fill(credentials["login"])
        password_field.fill(credentials["password"])
        submit_button.click()
        # URL frouxa: o LinkedIn redireciona pro feed com querystring variável.
        # Timeout aqui não é erro: quase sempre é checkpoint/captcha, e o
        # diagnóstico útil está logo abaixo.
        try:
            page.wait_for_url("**/feed/**", timeout=WAIT_FOR_URL_TIMEOUT)
        except Exception:
            pass

        if FEED_URL in page.url:
            print("Login bem-sucedido com credenciais.")
            return True
        else:
            print("Falha no login. URL atual:", page.url)
            page.screenshot(path="login_failure.png")
            if "checkpoint" in page.url:
                print("CAPTCHA detectado. Intervenção manual necessária.")
            elif page.query_selector("text=Incorrect email or password") or page.query_selector("text=Não foi possível fazer login"):
                print("Credenciais fornecidas inválidas.")
            return False
    except Exception as em:
        print(f"Erro no login: {em}")
        page.screenshot(path="login_error.png")
        return False

def save_new_token(context, credentials):
    """Salva um novo token de autenticação após login bem-sucedido."""
    cookies = context.cookies()
    auth_token = next((cookie["value"] for cookie in cookies if cookie["name"] == "li_at"), None)
    if auth_token:
        credentials["auth"] = [auth_token]
        save_credentials(credentials)
        print("Novo token de autenticação capturado e salvo.")

def try_login(page):
    """Tenta fazer login usando a Page já aberta no contexto do Core."""
    credentials = load_credentials()
    if not are_credentials_valid(credentials):
        print("Erro: Credenciais não fornecidas no arquivo JSON.")
        return False

    token = get_auth_token(credentials)
    if token and attempt_token_login(page.context, page, token):
        return True

    # Token falhou → limpa e tenta com credenciais
    credentials["auth"] = []
    save_credentials(credentials)
    page.context.clear_cookies()

    if attempt_credential_login(page, credentials):
        save_new_token(page.context, credentials)
        return True

    print("Falha no login com credenciais.")
    return False
