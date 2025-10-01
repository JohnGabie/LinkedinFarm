from core.orchestrator import BrowserOrchestrator
from shared.database.database_manager import upsert_contact, mark_invited, load_db

my_connection = "https://www.linkedin.com/mynetwork/invite-connect/connections/"

def main():
    orch = BrowserOrchestrator.instance()
    page = orch.open_page()
    try:
        print("Login attempt: Success")

        print(f"Navigating to search URL: {my_connection}")
        page.goto(my_connection)
        page.wait_for_load_state("domcontentloaded")

        title = page.title()
        print(f"Page title: {title}")

        print("Executando Bot de conexão inicial...")

    finally:
       orch.close_page(orch)


if __name__ == '__main__':
    main()



# # inserir/atualizar
# upsert_contact({
#     "profile_url": "https://linkedin.com/in/johndoe",
#     "name": "John Doe",
#     "company": "Tech Corp",
#     "position": "Recruiter"
# })
#
# # marcar como convidado
# mark_invited("https://linkedin.com/in/johndoe")
#
# # carregar tudo
# df = load_db()
# print(df)

