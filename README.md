<div align="center">

# 🌾 LinkedinFarm

### Suite de Automação Inteligente para o LinkedIn

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

> **⚠️ Status: Em Desuso**
> O LinkedIn reforçou significativamente seus mecanismos anti-bot ao longo de 2024/2025. As funcionalidades de automação descritas aqui estão atualmente bloqueadas pelas novas proteções da plataforma. O projeto permanece público como referência de arquitetura e estudo de automação web com Python.

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

| Módulo | Responsabilidade |
|--------|-----------------|
| `conexao-bot` | Envia convites de conexão automaticamente para recrutadores, profissionais de RH e figuras estratégicas da sua área |
| `verify-my-connection-bot` | Monitora e valida conexões existentes, filtrando contatos relevantes |
| `core/orchestrator` | Gerencia o ciclo de vida dos bots, coordenando sessões de navegador e abas como um singleton thread-safe |
| `core/session_manager` | Mantém sessões autenticadas no LinkedIn, evitando logins repetidos |
| `core/tab_manager` | Controla múltiplas abas do navegador para paralelizar ações |
| `shared/database` | Camada de persistência centralizada para histórico de ações e conexões |
| `shared/linkedin` | Utilitários compartilhados: login, busca de perfis e scraping de dados |

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

## 🛠️ Tecnologias Utilizadas

### Linguagem & Runtime
- **Python 3.12** — linguagem principal de todos os módulos

### Automação de Navegador
- **Playwright** — automação moderna de browser com suporte a Chromium headless
- **Selenium + WebDriver Manager** — camada adicional de controle do navegador

### Infraestrutura
- **Docker** — containerização completa do ambiente, garantindo reprodutibilidade em qualquer máquina
- **Docker Compose** — orquestração dos serviços com variáveis de ambiente e volumes mapeados

### Utilitários Python
- **python-dotenv** — gerenciamento de variáveis de ambiente via `.env`
- **requests** — requisições HTTP para integrações externas
- **pytest + pytest-playwright** — suite de testes de automação

---

## 🚀 Como Instalar

### Pré-requisitos

- [Docker](https://www.docker.com/get-started) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/install/) disponível
- Conta no LinkedIn

### Passo a Passo

**1. Clone o repositório**

```bash
git clone https://github.com/JohnGabie/LinkedinFarm.git
cd LinkedinFarm
```

**2. Configure suas credenciais**

Crie um arquivo `.env` na raiz do projeto:

```env
LINKEDIN_EMAIL=seu_email@exemplo.com
LINKEDIN_PASSWORD=sua_senha_aqui
```

> 🔒 O arquivo `.env` já está no `.gitignore`. Nunca suba suas credenciais para o repositório.

**3. Suba o container**

```bash
docker-compose up --build
```

O Docker vai automaticamente:
- Baixar a imagem base do Python 3.12 Slim
- Instalar todas as dependências do `requirements.txt`
- Instalar o Chromium via Playwright
- Iniciar o bot

---

## 📖 Como Utilizar

### Executando via Docker (recomendado)

```bash
# Iniciar em background
docker-compose up -d

# Acompanhar os logs em tempo real
docker-compose logs -f

# Parar os containers
docker-compose down
```

### Executando localmente (sem Docker)

```bash
# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale o browser do Playwright
playwright install chromium

# Execute o bot de conexões
python conexao-bot/bot.py
```

### Configurando os alvos do `conexao-bot`

Dentro de `conexao-bot/bot.py`, ajuste os parâmetros de busca conforme seu objetivo:

```python
search_query = "Recrutador TI"  # Termo de busca (ex: "HR Manager", "Tech Recruiter")
max_connections = 200           # Limite de convites por execução
max_pages = 100                 # Páginas de resultados a percorrer
```

---

## 📁 Estrutura do Projeto

```
LinkedinFarm/
├── conexao-bot/               # Bot de envio de convites de conexão
│   ├── bot.py
│   └── config/
├── verify-my-connection-bot/  # Bot de verificação de conexões
│   └── src/
├── core/                      # Núcleo de orquestração
│   ├── orchestrator.py        # Singleton thread-safe que gerencia o browser
│   ├── session_manager.py     # Gerenciamento de sessão autenticada
│   ├── tab_manager.py         # Controle de abas do navegador
│   └── keep_alive.py          # Mantém a sessão ativa
├── shared/                    # Módulos compartilhados entre os bots
│   ├── database/              # Camada de persistência de dados
│   └── linkedin/              # Utilitários do LinkedIn (login, busca, scraping)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## ⚠️ Aviso Legal

Este projeto foi desenvolvido exclusivamente para fins **educacionais e de estudo** em automação de browsers com Python. O uso de bots pode violar os [Termos de Serviço do LinkedIn](https://www.linkedin.com/legal/user-agreement). O autor não se responsabiliza por suspensões de conta ou quaisquer consequências decorrentes do uso desta ferramenta. Use com responsabilidade.

---

<div align="center">

Feito com 🧠 e muita vontade de não preencher formulários manualmente.

**[⭐ Deixe uma estrela se o projeto te inspirou!](https://github.com/JohnGabie/LinkedinFarm)**

</div>
