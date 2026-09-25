# Seletores da tela de login do LinkedIn.
#
# Os antigos (input#username, input#password, button[type=submit]) morreram:
# hoje os ids são ofuscados e trocam a cada carregamento, não existe <form>
# e nenhum botão é type=submit. Sobrou o type dos inputs — e mesmo esses
# precisam ser filtrados por visibilidade, porque a página renderiza um par
# oculto antes do par real.
#
# Para o botão "Entrar" não há seletor estável: use
# core.handle.try_login.find_submit_button(page).
LI_LOGIN_EMAIL = "input[type='email']"        # usar sempre o primeiro VISÍVEL
LI_LOGIN_PASSWORD = "input[type='password']"  # usar sempre o primeiro VISÍVEL
