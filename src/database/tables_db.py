from src.database.db import executar_modif

def init_db():

    executar_modif("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            nome TEXT,
            cpf_cnpj TEXT,
            email TEXT,
            estado TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS fila_emissao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'pendente',
            payload TEXT NOT NULL,
            tentativas INTEGER DEFAULT 0,
            erro TEXT,
            idempotency_key TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processado_em TIMESTAMP     
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL REFERENCES users(phone),
            status TEXT NOT NULL DEFAULT 'COLLECTING', -- COLLECTING | CONFIRMING | EMITTING | DONE | ERROR | CANCELLED
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL, -- 'user' | 'assistant'
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS nfse_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL UNIQUE REFERENCES conversations(id) ON DELETE CASCADE,
            nf TEXT NOT NULL DEFAULT '{}', -- JSON
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS nfse_emitidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL UNIQUE REFERENCES conversations(id) ON DELETE CASCADE,
            numero_nota TEXT,
            protocolo TEXT,
            dados_enviados TEXT NOT NULL, -- JSON: payload exato enviado para a API fiscal
            resposta_api TEXT NOT NULL, -- JSON: payload exato enviado para a API fiscal
            emitida_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE INDEX idx_conversations_wpp_status
            ON conversations(phone, status)
    """)

    executar_modif("""
        CREATE INDEX idx_messages_conversations
            ON messages(conversation_id)
    """)

    executar_modif("""
        CREATE INDEX idx_nfse_emitidas_conversation
            ON nfse_emitidas(conversation_id)
    """)