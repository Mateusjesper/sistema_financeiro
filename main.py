from app.banco import criar_tabelas, popular_dados_iniciais, criar_usuario_admin, popular_categorias
from app.gui.login import iniciar_login

if __name__ == "__main__":
    criar_tabelas()
    popular_dados_iniciais()
    criar_usuario_admin()
    popular_categorias()
    iniciar_login()