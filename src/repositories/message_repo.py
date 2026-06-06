import sqlite3
from src.database.db import executar_modif

# def salvar_msg_se_nova(phone, tipo, mensagem_id, conteudo, timestamp):

#     if not mensagem_id:
#         print("mensagem sem ID, ignorando\n")
#         return False

#     try:
#         executar_modif(
#             """
#             INSERT INTO messages (phone, tipo, mensagem_id, conteudo, timestamp)
#             VALUES (?, ?, ?, ?, ?)
#             """,
#             (phone, tipo, mensagem_id, conteudo, timestamp)
#         )
#         print("mensagem do usuario é nova e foi salva no db\n")
#         return True
    
#     except sqlite3.IntegrityError:
#         print("mensagem duplicada ignorada\n")
#         return False

# def limpar_msg_antigas():

#     msg_deletadas = executar_modif(
#         """
#         DELETE FROM messages
#         WHERE criado_em < datetime('now', '-1 day')
#         """
#     )

#     if msg_deletadas > 0:
#         print(f"{msg_deletadas} messages antigas foram deletadas\n")