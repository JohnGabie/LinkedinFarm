<div align="center">

# 🌾 LinkedinFarm

### Suite de Automação Inteligente para o LinkedIn

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

> ### 🏁 Última atualização — 24/09/2026
>
> **Este é o commit final do LinkedinFarm.** O repositório fica no ar como
> referência de arquitetura e como registro de um problema de engenharia que
> valeu a pena resolver: reviver uma automação de browser depois que a
> plataforma alvo reconstruiu a interface inteira por baixo dela.
>
> **O projeto continua em [claudia-rh](https://github.com/JohnGabie/claudia-rh).**
> A ideia original — tirar a burocracia da busca por emprego do caminho de
> quem procura — segue lá, com escopo maior e arquitetura nova.
>
> A versão que está aqui **funciona**: foi executada de ponta a ponta e
> validada contra o LinkedIn real na data acima. Mas a validade tem prazo —
> veja [Por que isso quebra](#-por-que-isso-quebra-e-vai-quebrar-de-novo).

---

## 🎯 O Problema que Motivou o Projeto

Quem já buscou emprego sabe bem: **procurar trabalho virou um trabalho em tempo integral**.

A rotina de todo candidato envolve:
- Enviar dezenas de convites para recrutadores e profissionais de RH todo dia
- Preencher manualmente formulários de candidatura — muitas vezes os mesmos campos repetidos em cada vaga
- Ficar de olho no feed do LinkedIn esperando novas oportunidades aparecerem
- Monitorar conexões e interações que podem abrir portas

Tudo isso **consome horas preciosas** que deveriam ser investidas em se preparar melhor, estudar e focar nas oportunidades que realmente importam.

O **LinkedinFarm** nasceu para automatizar essa burocracia, deixando você livre para o que realmente vale.

> *"Porque buscar emprego não precisa ser um trabalho em tempo integral."*

---

## 🤖 O que o Projeto Faz

O LinkedinFarm é uma **suite modular de bots** que opera sobre o LinkedIn de forma autônoma. Cada módulo tem uma responsabilidade bem definida:

| Módulo | Responsabilidade | Estado |
|--------|-----------------|--------|
| `conexao-bot` | Envia convites de conexão automaticamente para recrutadores, profissionais de RH e figuras estratégicas da sua área | ✅ funcional |
| `verify-my-connection-bot` | Monitora e valida conexões existentes | ⚠️ esqueleto — navega e autentica, lógica de leitura ainda não implementada |
| `core/orchestrator` | Gerencia o ciclo de vida dos bots, coordenando sessões de navegador e abas como um singleton thread-safe | ✅ funcional |
| `core/session_manager` | Mantém a sessão autenticada, com fallback para login manual na janela | ✅ funcional |
| `core/tab_manager` | Controla múltiplas abas do navegador | ✅ funcional |
| `shared/database` | Persistência em planilha (pandas + openpyxl) | ✅ funcional, não integrado ao fluxo |
| `shared/linkedin` | Seletores compartilhados | ✅ funcional |

### Fluxo de Operação

```
┌─────────────────────────────────────────────────┐
│                  Orchestrator                   │
│  (Gerencia sessões e coordena os módulos)       │
└───────────┬──────────────┬───────────────────────┘
            │              │
    ┌───────▼──────┐  ┌────▼───────────────────┐
    │  conexao-bot │  │  verify-connection-bot  │
    │  (Convites)  │  │  (Validação de rede)    │
    └───────┬──────┘  └────────────────────────┘
            │
    ┌───────▼──────────────────────┐
    │  shared / database           │
    │  (Persistência e histórico)  │
    └──────────────────────────────┘
```

---

## 🧨 Por que isso quebra (e vai quebrar de novo)

Em 2026 o LinkedIn migrou login e busca de pessoas para **Server-Driven UI**.
Na prática, isso apagou do mapa todo seletor baseado em classe ou id:

- as classes viraram hashes que **rodam a cada deploy** (`_9cd37f2c`, `e078840b`…)
- os `id` dos inputs são ofuscados e **mudam a cada carregamento** da página
- **não existe mais `<form>`** na tela de login, nem nenhum `button[type=submit]`
- a página de login renderiza um **par de inputs invisível antes do par real** —
  um seletor ingênuo preenche o campo fantasma e parece funcionar até falhar

Dos seletores originais do projeto, **3/3 do login e 7/7 da busca** pararam de
casar. A regra que sobreviveu à reescrita: **nunca ancore em classe ou id.**
Só em atributo semântico, papel de acessibilidade, ou geometria.

| O que o bot usava antes | Hoje | Âncora nova |
|---|---|---|
| `input[name='session_key']` | ☠️ | `input[type='email']` + filtro de visibilidade |
| `button[type='submit']` | ☠️ | único botão visível sem ícone abaixo da senha |
| `div[data-chameleon-result-urn]` | ☠️ | `[data-testid='lazy-column']` |
| `button:has-text('Conectar')` | ☠️ | `a[href*='/search-custom-invite/']` |
| `span[dir='ltr']` (nome) | ☠️ | `a[href*='/in/']` dentro do cartão |
| `div.t-14.t-black.t-normal` (cargo) | ☠️ | `span:not([class])` |
| `button:has-text('Enviar sem nota')` | ✅ sobreviveu | mantido |

Repare que o "Conectar" deixou de ser `<button>` e virou `<a href=".../search-custom-invite/?vanityName=...">`.
Ficou **melhor** que antes: o `href` é semântico, independe de idioma e ainda
entrega o slug do perfil de graça.

### O bug que só aparece rodando

Metade dos convites falhava. Não era seletor: era **ritmo**. O loop disparava
os cliques encostados um no outro e o modal de confirmação não acompanhava.
Medido: **~50% de falha sem pausa, 0% com 1,5s** (`DELAY_BETWEEN_INVITES_MS`).

Nenhuma leitura de código mostraria isso. Só rodando.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12** — linguagem principal
- **Playwright** — automação de browser com contexto persistente (a sessão
  autenticada sobrevive entre execuções)
- **pandas + openpyxl** — camada de persistência em planilha
- **python-dotenv** — credenciais via `.env`
- **pytest + pytest-playwright** — dependências de teste

O `Dockerfile` e o `docker-compose.yml` continuam no repositório, mas
**não funcionam** — veja [Docker](#-docker-quebrado).

---

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.12
- Conta no LinkedIn

### Passo a passo

```bash
git clone https://github.com/JohnGabie/LinkedinFarm.git
cd LinkedinFarm

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
playwright install chromium
```

### Credenciais

```bash
cp .env.example .env
```

Preencha o `.env`:

```env
LINKEDIN_EMAIL=seu_email@exemplo.com
LINKEDIN_PASSWORD=sua_senha_aqui
```

> 🔒 O `.env` está no `.gitignore` — verificado com `git check-ignore`, junto de
> `connections.json`, `profiles.json` e `core/.user_data`.

**Não quer colocar a senha em arquivo?** Rode `python core/keep_alive.py`, faça
o login na janela do Chromium que abrir, e pronto: a sessão fica salva em
`core/.user_data` e os bots reusam. Essa é a via mais segura — e o LinkedIn vê
um login humano, com bem menos chance de captcha que o preenchimento automático.

### Executando

```bash
python conexao-bot/bot.py
```

Roda de qualquer diretório — os entrypoints resolvem o `sys.path` sozinhos.

**Comece pequeno.** O limite de convites é configurável por variável de
ambiente, sem editar o código:

```bash
MAX_CONNECTIONS=5 python conexao-bot/bot.py
```

O contador é cumulativo e fica em `connections.json`, então execuções
seguintes retomam de onde pararam. O alvo da busca ainda é editado direto no
`conexao-bot/bot.py`:

```python
search = LinkedInSearch("Dell", "1")   # termo de busca e página inicial
```

### 🐳 Docker (quebrado)

O caminho Docker **não sobe**, e ficou documentado em vez de corrigido:

- `Dockerfile:42` — `CMD ["python", "src/bot.py"]` aponta para um caminho que
  não existe na imagem
- `Dockerfile:8-26` — os pacotes do `apt-get` usam nomes pré-transição t64
  (`libasound2`, `libatk1.0-0`, `libcups2`…), renomeados para `*t64` na
  `python:3.12-slim` atual (Debian 13)
- `docker-compose.yml:11-12` — monta `./profiles.json` e `./connections.json`,
  que não existem no repo; o Docker cria *diretórios* com esses nomes

---

## 📁 Estrutura do Projeto

```
LinkedinFarm/
├── conexao-bot/               # Bot de envio de convites de conexão
│   ├── bot.py
│   └── config/
│       ├── button_handler.py      # seletores da busca + envio do convite
│       ├── linkedin_search.py     # construtor da URL de busca
│       └── web_scraper_profiles.py
├── verify-my-connection-bot/  # Bot de verificação de conexões (esqueleto)
│   └── src/
├── core/                      # Núcleo de orquestração
│   ├── orchestrator.py        # Singleton thread-safe que gerencia o browser
│   ├── session_manager.py     # Sessão autenticada + login manual
│   ├── tab_manager.py         # Controle de abas do navegador
│   ├── keep_alive.py          # Abre o browser e segura a sessão
│   └── handle/try_login.py    # Login por token, credenciais ou manual
├── shared/
│   ├── database/              # Persistência (pandas/openpyxl)
│   └── linkedin/selectors.py
├── .env.example
└── requirements.txt
```

---

## ⚠️ Aviso Legal

Este projeto foi desenvolvido exclusivamente para fins **educacionais e de estudo** em automação de browsers com Python. O uso de bots pode violar os [Termos de Serviço do LinkedIn](https://www.linkedin.com/legal/user-agreement). O autor não se responsabiliza por suspensões de conta ou quaisquer consequências decorrentes do uso desta ferramenta. Use com responsabilidade — e comece com `MAX_CONNECTIONS` baixo.

---

<div align="center">

### 👉 A continuação está em [**claudia-rh**](https://github.com/JohnGabie/claudia-rh)

Feito com 🧠 e muita vontade de não preencher formulários manualmente.

**João Gabriel**
[LinkedIn](https://www.linkedin.com/in/joaogabie/) · [GitHub](https://github.com/JohnGabie)

</div>
