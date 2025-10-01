from urllib.parse import urlencode

class LinkedInSearch:
    def __init__(self, keywords, page, base_url="https://www.linkedin.com/search/results/people/"):
        """
        Inicializa a classe LinkedInSearch com keywords e page obrigatórios.

        :param keywords: As palavras-chave de busca (ex.: 'tech recruiter')
        :param page: O número da página inicial (ex.: '1' ou 1)
        :param base_url: A URL base para a busca (opcional)
        """
        self.base_url = base_url
        self.params = {
            "keywords": keywords,
            "origin": "GLOBAL_SEARCH_HEADER",
            "page": str(page),  # Converte page para string, aceitando int ou str
            "sid": "fJ%2C"
        }

    def set_keywords(self, keywords):
        """Define novas palavras-chave de busca."""
        self.params["keywords"] = keywords

    def set_page(self, page):
        """Define um novo número de página."""
        self.params["page"] = str(page)

    def get_url(self):
        """Gera a URL completa com os parâmetros atuais."""
        encoded_params = urlencode(self.params)
        return f"{self.base_url}?{encoded_params}"

    def update_search(self, keywords=None, page=None):
        """Atualiza os parâmetros de busca e retorna a nova URL."""
        if keywords:
            self.set_keywords(keywords)
        if page:
            self.set_page(page)
        return self.get_url()

# Exemplo de uso
if __name__ == "__main__":
    # Cria uma instância com keywords e page obrigatórios
    search = LinkedInSearch("tech recruiter", "1")
    print("URL de busca padrão:", search.get_url())

    # Atualiza a busca
    url = search.update_search(keywords="RH", page="2")
    print("URL de busca atualizada:", url)