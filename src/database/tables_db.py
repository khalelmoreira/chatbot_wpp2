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

    executar_modif("""
        CREATE TABLE IF NOT EXISTS tomador (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            prestador_id INTEGER NOT NULL REFERENCES pretador(id),
                   
            -- identificacao
                   
            nome         TEXT NOT NULL,
            cnpj         TEXT,
            cpf          TEXT,
            email        TEXT,
            phone        TEXT,
                   
            --endereco
                   
            logradouro   TEXT,
            numero       TEXT,
            complemento  TEXT,
            bairro       TEXT,
            cidade       TEXT,
            uf           TEXT,
            cep          TEXT,

            created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE (prestador_id, cnpj),
            UNIQUE (prestador_id, cpf),
            CHECK(cnpj IS NOT NULL OR cpf IS NOT NULL)
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS nfs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            prestador_id  INTEGER NOT NULL REFERENCES prestadores(id),
            tomador_id    INTEGER NOT NULL REFERENCES tomadores(id),
                   
            -- controle de emissão
                   
            notaas_invoice_id  TEXT UNIQUE,          -- preenchido no 202
            idempotency_key    TEXT UNIQUE NOT NULL, -- sha256(payload + prestador_id)
            status             TEXT NOT NULL DEFAULT 'queued',  -- queued | processing | issued | error | cancelled
                   
            -- payload enviado (campos explícitos + blob completo)
                   
            -- OBRIGATORIOS                   
                -- tomador                   
                    nome               TEXT NOT NULL,
                    cnpj               TEXT NOT NULL,
                    
                -- servico                   
                    descricao_servico  TEXT NOT NULL,
                
                -- valores                   
                    aliquota_iss       REAL,
                    valor_total        REAL NOT NULL,
                   
            cpf          TEXT,
            email        TEXT,
            phone        TEXT,
                   
                --endereco
                   
            logradouro   TEXT,
            numero       TEXT,
            complemento  TEXT,
            bairro       TEXT,
            cidade       TEXT,
            uf           TEXT,
            cep          TEXT,
                   
            codigo_servico     TEXT,                 -- cTribNac
            iss_retido         INTEGER DEFAULT 0,    -- boolean
            competencia        TEXT,                 -- YYYY-MM
            referencia         TEXT,                 -- seu ID externo
            payload_enviado    TEXT NOT NULL,        -- JSON completo
                   
            -- campos preenchidos por webhook/polling (issued)
                   
            ch_nfse            TEXT,                 -- chNFSe / código de verificação
            numero_nfse        TEXT,                 -- nNFSe
            ambiente           TEXT,                 -- "producao" | "homologacao"
            pdf_url            TEXT,
            xml_url            TEXT,
            documents_cached   INTEGER,              -- boolean
            document_status    TEXT,                 -- "partial" | "complete"
            emitido_em         TEXT,                 -- emittedAt ISO 8601
                   
            -- campos preenchidos por webhook/polling (error)
                   
            erro_codigo        TEXT,
            erro_mensagem      TEXT,
            erros_json         TEXT,                 -- array [{Codigo, Descricao, Complemento}]
                   
            -- campos preenchidos por webhook/polling (cancelled)
                   
            cancelado_em       TEXT,
            cancel_xml_url     TEXT,

            requested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS webhook_ntaas_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id TEXT UNIQUE NOT NULL,  -- X-Notaas-Delivery; chave de idempotência
            evento      TEXT NOT NULL,         -- nfse.issued | nfse.error | nfse.cancelled | nfse.documents_ready | batch.completed
            invoice_id  TEXT,                  -- data.invoiceId quando aplicável
            payload     TEXT NOT NULL,         -- JSON bruto completo
            recebido_em TEXT NOT NULL DEFAULT (datetime('now'))
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