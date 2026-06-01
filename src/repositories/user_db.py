from typing import Optional
from src.repositories.db import fetchone, executar_modif
from src.types.context_base import User, EstadoUser
from src.types.context_cadastro import ContextCadastro, DadosCadastro

def verifica_estado_usuario(phone: str) -> Optional[User]:

    row = fetchone(
        """
        SELECT id, phone, estado
        FROM usuarios
        WHERE phone = ?
        LIMIT 1
        """,
        (phone,)
    )

    print(f"VERIFICA ESTADO USER [ROW]: {row}\n")

    if not row:
        return None
    
    estado = row["estado"] or "novo"

    return User(
        id=row["id"],
        phone=row["phone"],
        estado=estado
    )

def criar_usuario(phone: str) -> User:

    executar_modif(
        """
        INSERT INTO usuarios (phone, estado, criado_em)
        VALUES (?, ?, datetime('now'))
        """,
        (phone, "aguardando_dados")
    )

    print(f"CRIANDO USER NO DB\n")

    user = verifica_estado_usuario(phone)

    if not user:
        raise ValueError("erro ao criar usuario")
    
    return User

def atualiza_estado_usuario(user: User, novo_estado: EstadoUser) -> None:

    query = """
        UPDATE usuarios
        SET estado = ?
        WHERE phone = ?
    """
    executar_modif(query, (novo_estado, user.phone))

def busca_dados_usuario(ctx: ContextCadastro) -> None:

    phone = ctx.user.phone

    query = """
        SELECT nome, cpf_cnpj, email
        FROM usuarios
        WHERE phone = ?
    """
    row = fetchone(query, (phone,))

    if not row:
        
        ctx.dados_db = DadosCadastro()

        return
    
    ctx.dados_db = DadosCadastro(
        nome=row["nome"],
        cpf_cnpj=row["cpf_cnpj"],
        email=row["email"]
    )

def atualizar_usuario_parcial(ctx: ContextCadastro) -> None:

    phone = ctx.user.phone
    dados_novos = ctx.dados_novos
    
    campos = []
    valores = []

    if dados_novos.nome:
        campos.append("nome = ?")
        valores.append(dados_novos.nome)
    
    if dados_novos.cpf_cnpj:
        campos.append("cpf_cnpj = ?")
        valores.append(dados_novos.cpf_cnpj)

    if dados_novos.email:
        campos.append("email = ?")
        valores.append(dados_novos.email)

    if not campos:
        return
    
    query = f"""
        UPDATE usuarios
        SET {", ".join(campos)}
        WHERE phone = ?
    """

    valores.append(phone)

    executar_modif(query, tuple(valores))