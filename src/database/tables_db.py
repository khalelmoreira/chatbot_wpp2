from src.database.db import DB

def init_db():

    db = DB()

    # PRESTADOR

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS prestador (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            phone                TEXT UNIQUE NOT NULL,
            status               TEXT,
            name                 TEXT,
            email                TEXT,
                      
            --dados fiscais
            cnpj                 TEXT UNIQUE,
            razao_social         TEXT,
            regime_tributario    TEXT, -- "1", "2", "3", "3e"
            
            -- endereço
            cep                  TEXT,
            logradouro           TEXT,
            numero               TEXT,
            complemento          TEXT,
            bairro               TEXT,
            cidade               TEXT,
            uf                   TEXT,

            -- notaas                   
            ntaas_project_id     TEXT,
            ntaas_api_key        TEXT,  --criptografaco
            org_token            TEXT,
            certificado_enviado  INTEGER DEFAULT 0,
                   
            -- controle
            error_msg            TEXT,
            created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # TOMADOR

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS tomador (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            prestador_id INTEGER NOT NULL REFERENCES prestador(id),
            created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            nome         TEXT NOT NULL,
                   
            -- identificacao
                   
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

            
            UNIQUE (prestador_id, cnpj),
            UNIQUE (prestador_id, cpf),
            CHECK(cnpj IS NOT NULL OR cpf IS NOT NULL)
        )
    """)

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS nfs (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                   
            -- NOT NULL
                   
            prestador_id       INTEGER NOT NULL REFERENCES prestador(id),
            tomador_id         INTEGER NOT NULL REFERENCES tomador(id),
            conversation_id    INTEGER NOT NULL UNIQUE REFERENCES conversations(id) ON DELETE CASCADE,
            idempotency_key    TEXT UNIQUE NOT NULL,                                        -- sha256(payload + prestador_id)
            status             TEXT NOT NULL DEFAULT 'QUEUED',    -- QUEUED | DONE | ERROR | CANCELLED
            tentativas         INTEGER NOT NULL DEFAULT 0,
            payload_enviado    TEXT NOT NULL,                                               -- JSON completo
            requested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   
            -- OBRIGATORIOS NFSe
                -- tomador
                    nome               TEXT NOT NULL,
                    cnpj               TEXT NOT NULL,
                    
                -- servico                   
                    descricao_servico  TEXT NOT NULL,
                
                -- valores                   
                    aliquota_iss       REAL DEFAULT 5.0,
                    valor_total        REAL NOT NULL,


            phone              TEXT,
            invoice_id         TEXT UNIQUE,          -- preenchido no 202
            cpf                TEXT,
            email              TEXT,
                   
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
                   
            -- campos preenchidos por webhook/polling (issued)
                   
            ch_nfse            TEXT,                 -- chNFSe / código de verificação
            n_nfse             TEXT,                 -- nNFSe
            issued_at          TEXT,
            ambiente           TEXT,                 -- "producao" | "homologacao"
            pdf_url            TEXT,
            xml_url            TEXT,
            documents_cached   INTEGER,              -- boolean
            document_status    TEXT,                 -- "partial" | "complete"
            emitido_em         TEXT,                 -- emittedAt ISO 8601
                   
            -- campos preenchidos por webhook/polling (error)
                   
            erro_code        TEXT,
            erro_msg         TEXT,
            erro_json        TEXT,                 -- array [{Codigo, Descricao, Complemento}]
                   
            -- campos preenchidos por webhook/polling (cancelled)
            
            processado_em      TIMESTAMP,
            cancelled_at       TEXT,
            cancel_xml_url     TEXT
        )
    """)

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS conversations (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            prestador_id        INTEGER NOT NULL REFERENCES prestador(id),
            phone               TEXT NOT NULL REFERENCES prestador(phone),
            status              TEXT NOT NULL,                          -- COLLECTING | CONFIRMING | QUEUED | DONE | ERROR | CANCELLED
            draft_json          TEXT NOT NULL DEFAULT '{}',
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            prestador_id    INTEGER NOT NULL REFERENCES prestador(id),
            phone           TEXT NOT NULL REFERENCES prestador(phone),
            role            TEXT NOT NULL, -- 'USER' | 'AI'
            content         TEXT NOT NULL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS ntaas_deliveries (
            delivery_id TEXT PRIMARY KEY,  -- X-Notaas-Delivery; chave de idempotência
            event       TEXT,              -- nfse.issued | nfse.error | nfse.cancelled | nfse.documents_ready | batch.completed | webhook.test
            invoice_id  TEXT,              -- data.invoiceId quando aplicável
            payload     TEXT,              -- JSON bruto completo
            recebido_em TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    db.executar_modif("""
        CREATE TABLE IF NOT EXISTS upload_tokens (
            token         TEXT PRIMARY KEY,
            prestador_id  INTEGER NOT NULL REFERENCES prestador(id),
            project_id    TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now')),
            expire_at     TEXT NOT NULL,
            used         INTEGER NOT NULL DEFAULT 0
        )
    """)

    db.executar_modif("""
        CREATE INDEX IF NOT EXISTS idx_conversations_wpp_status
            ON conversations(phone, status)
    """)

    db.executar_modif("""
        CREATE INDEX IF NOT EXISTS idx_prestador_phone
            ON prestador(phone)
    """)