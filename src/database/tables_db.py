from src.database.db import executar_modif

def init_db():

    executar_modif("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            phone         TEXT UNIQUE NOT NULL,
            name          TEXT,
            estado        TEXT NOT NULL DEFAULT 'novo',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # PRESTADOR

    executar_modif("""
        CREATE TABLE IF NOT EXISTS prestador (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            phone                TEXT UNIQUE REFERENCES users(phone),
            
            --dados fiscais
            cnpj                 TEXT UNIQUE,
            razao_social         TEXT,
            inscricao_municipal  TEXT,
            regime_tributario    TEXT, -- "1", "2", "3", "3e"
            email                TEXT,
            
            -- endereço
            cep                  TEXT,
            logradouro           TEXT,
            numero               TEXT,
            complemento          TEXT,
            bairro               TEXT,
            cidade               TEXT,
            uf                   TEXT,

            -- notaas                   
            notaas_project_id    TEXT,
            notaas_api_key       TEXT,  --criptografaco
            certificado_enviado  INTEGER NOT NULL DEFAULT 0,
                   
            -- controle
            onboarding_status    TEXT NOT NULL DEFAULT 'novo',
            created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # TOMADOR

    # executar_modif("""
    #     CREATE TABLE IF NOT EXISTS tomador (
    #         id           INTEGER PRIMARY KEY AUTOINCREMENT,
    #         prestador_id INTEGER NOT NULL,
    #         nome         TEXT,
    #         cnpj         TEXT,
    #         email        TEXT,
    #         tipo_pessoa  TEXT, -- "F" OU "J"
    #         created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
    #         FOREING KEY (prestador_id) REFERENCES prestador(id),
    #         UNIQUE (prestador_id, cnpj)
    #     )
    # """)

    # NF EMITIDA

    # executar_modif("""
    #     CREATE TABLE IF NOT EXISTS emissoes (
    #         id               INTEGER PRIMARY KEY AUTOINCREMENT,
    #         prestador_id     INTEGER NOT NULL,
    #         tomador_id       INTEGER NOT NULL,
    #         invoice_id       TEXT UNIQUE, --retorno de notaas
    #         idempotency_key  TEXT UNIQUE, --sha256 gerado
    #         status           TEXT DEFAULT 'pendente',
    #         valor_total      REAL,
    #         descricao        TEXT,
    #         created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
    #         FOREING KEY (prestador_id) REFERENCES prestador(id),
    #         UNIQUE (tomador_id) REFERENCES tomador(id)
    #     )
    # """)

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
        CREATE INDEX IF NOT EXISTS idx_conversations_wpp_status
            ON conversations(phone, status)
    """)

    executar_modif("""
        CREATE INDEX IF NOT EXISTS idx_messages_conversations
            ON messages(conversation_id)
    """)

    executar_modif("""
        CREATE INDEX IF NOT EXISTS idx_nfse_emitidas_conversation
            ON nfse_emitidas(conversation_id)
    """)

    executar_modif("""
        CREATE INDEX IF NOT EXISTS idx_prestador_phone
            ON prestador(phone)
    """)