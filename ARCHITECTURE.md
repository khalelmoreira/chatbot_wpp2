# Arquitetura do ChatBot WhatsApp

## 📐 Estrutura de Camadas

O projeto segue a arquitetura em camadas (Layered Architecture), otimizada para MVPs:

```
┌─────────────────────────────────────────┐
│           Controllers (HTTP)             │
│  - webhook_controller.py                 │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│             Services (Business Logic)    │
│  - ai_service.py                        │
│  - msg_service.py                       │
│  - audio_service.py                     │
│  - nfse_service.py                      │
│  - webhook_wpp.py                       │
│  - webhook_notaas.py                    │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│        Repositories (Data Access)        │
│  - base_repository.py                   │
│  - user_repository.py                   │
│  - msg_repository.py                    │
│  - nfse_repository.py                   │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Database (Persistence)          │
│  - connection.py (SQLite)               │
│  - whatsapp.db                          │
└─────────────────────────────────────────┘

Utils (Cross-cutting concerns)
├── logger.py (Logging centralizado)
├── error_handler.py (Tratamento de erros)
└── validators.py (Validações)
```

## 📂 Estrutura de Pastas

```
chatbot_wpp/
├── app.py                           # Entry point
├── config.py                        # Configurações globais
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py            # Gerenciamento de conexão
│   │   └── whatsapp.db             # Banco de dados
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic models para validação
│   │   └── mensagens.py            # Mensagens padrão
│   │
│   ├── repositories/               # Data Access Layer
│   │   ├── __init__.py
│   │   ├── base_repository.py     # CRUD base
│   │   ├── user_repository.py     # Operações de usuários
│   │   ├── msg_repository.py      # Operações de mensagens
│   │   └── nfse_repository.py     # Operações de NFSe
│   │
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── ai_service.py          # Integração OpenAI
│   │   ├── msg_service.py         # Envio de mensagens
│   │   ├── audio_service.py       # Transcrição de áudio
│   │   ├── nfse_service.py        # Lógica de NFSe
│   │   ├── webhook_wpp.py         # Processamento WhatsApp
│   │   ├── webhook_notaas.py      # Processamento Notaas
│   │   └── fila.py                # Fila de processamento
│   │
│   ├── controllers/               # HTTP Handlers
│   │   ├── __init__.py
│   │   └── webhook_controller.py  # Orquestração de webhooks
│   │
│   ├── utils/                     # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── logger.py              # Logging centralizado
│   │   ├── error_handler.py       # Tratamento de erros
│   │   └── validators.py          # Validações reutilizáveis
│   │
│   ├── flows/                     # Lógica de fluxo conversacional
│   │   ├── aguardando_dados.py
│   │   └── user_ativo.py
│   │
│   ├── templates/                 # Frontend
│   │   ├── form.html
│   │   ├── index.html
│   │   └── layout.html
│   │
│   ├── tests/                     # Testes unitários
│   │   └── ...
│   │
│   └── requirements.txt
│
└── logs/                           # Logs da aplicação (criado automaticamente)
    └── chatbot_YYYYMMDD.log
```

## 🔄 Fluxo de Requisição

### Webhook do WhatsApp

```
1. POST /webhook
   ↓
2. app.py → webhook_wpp() route
   ↓
3. webhook_controller.process_webhook()
   ↓
4. Extrai e valida mensagem (webhook_wpp service)
   ↓
5. MessageRepository.save_if_new()
   ↓
6. ai_service.analisar_mensagem_ia() (se necessário)
   ↓
7. UserRepository.update_user_status()
   ↓
8. msg_service.enviar_mensagem() (resposta)
   ↓
9. Retorna 200 OK
```

## 🎯 Padrões de Design Utilizados

### 1. **Repository Pattern**
- Abstrai acesso ao banco de dados
- Facilita testes (mockar repositories)
- Permite trocar BDD sem mudanças no resto do código

```python
# Uso
user_repo = UserRepository()
user = user_repo.find_user_by_phone("+5511999999999")
```

### 2. **Dependency Injection**
- Controllers injetam repositories
- Services recebem dependências como parâmetros
- Facilita testes unitários

```python
class WebhookController:
    def __init__(self):
        self.user_repo = UserRepository()
        self.msg_repo = MessageRepository()
```

### 3. **Service Layer**
- Centraliza lógica de negócio
- Reutilizável em múltiplos contextos (HTTP, Workers, etc)
- Fácil testar isoladamente

```python
# Mesmo serviço usado em diferentes contextos
ai_service.analisar_mensagem_ia(texto)  # Webhook
ai_service.analisar_mensagem_ia(texto)  # Worker
ai_service.analisar_mensagem_ia(texto)  # Testes
```

### 4. **Exception Handling Centralizado**
- AppError base para todas as exceções
- ErrorHandler registra erro handlers no Flask
- Logger automático de erros

```python
try:
    # código
except AppError as e:
    return ErrorHandler.handle_error(e)  # Trata automaticamente
```

### 5. **Logging Centralizado**
- Instância única de logger
- Log automático em arquivo e console
- Níveis de log apropriados

```python
from app.utils import logger

logger.info("Mensagem recebida")
logger.error("Erro ao processar", exc_info=True)
```

## 🚀 Como Expandir a Arquitetura

### Adicionar Nova Entidade

1. **Criar Schema** em `app/models/schemas.py`:
```python
class NovaEntidade(BaseModel):
    campo1: str
    campo2: Optional[int] = None
```

2. **Criar Repository** em `app/repositories/nova_repository.py`:
```python
class NovaRepository(BaseRepository):
    def _get_table_name(self) -> str:
        return "nova_entidade"
```

3. **Criar Service** em `app/services/nova_service.py`:
```python
class NovaService:
    def __init__(self):
        self.repo = NovaRepository()
    
    def fazer_algo(self):
        # Lógica de negócio
```

4. **Usar no Controller**:
```python
service = NovaService()
resultado = service.fazer_algo()
```

## ✅ Benefícios da Arquitetura

| Aspecto | Benefício |
|--------|-----------|
| **Separação de responsabilidades** | Cada camada tem um propósito claro |
| **Testabilidade** | Fácil mockar e testar isoladamente |
| **Manutenibilidade** | Novo dev encontra código estruturado |
| **Escalabilidade** | Adicionar features sem refatoração |
| **Reusabilidade** | Serviços usáveis em múltiplos contextos |
| **Debugging** | Logger centralizado e erro handlers |

## 📋 Tabelas do Banco de Dados

### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    phone TEXT UNIQUE,
    nome TEXT,
    cpf_cnpj TEXT,
    email TEXT,
    status TEXT DEFAULT 'aguardando_dados',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    user_phone TEXT,
    message_id TEXT UNIQUE,
    content TEXT,
    message_type TEXT,
    is_from_user BOOLEAN,
    created_at TIMESTAMP,
    FOREIGN KEY (user_phone) REFERENCES users(phone)
)
```

### nfses
```sql
CREATE TABLE nfses (
    id INTEGER PRIMARY KEY,
    user_phone TEXT,
    nfse_number TEXT,
    tomador_nome TEXT,
    tomador_cnpj TEXT,
    servico_descricao TEXT,
    valor_total REAL,
    status TEXT DEFAULT 'rascunho',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_phone) REFERENCES users(phone)
)
```

## 🔧 Configuração de Ambiente

```env
# Flask
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# WhatsApp
VERIFY_TOKEN=seu_token_verificacao
ACCESS_TOKEN=seu_access_token
PHONE_NUMBER_ID_TEST_META=seu_phone_id
API_META_VERSION=v18.0

# OpenAI
OPENAI_API_KEY=sk-xxxxx

# Notaas
WEBHOOK_SECRET_NOTAAS=seu_secret
```

## 📝 Próximos Passos

1. **Implementar flows conversacionais** - Expandir `flows/`
2. **Adicionar persistência de rascunhos** - NFSe drafts
3. **Implementar queue/worker** - Para processamento assíncrono
4. **Adicionar autenticação** - Para proteger endpoints
5. **Implementar cache** - Para melhor performance
6. **Adicionar testes** - Cobertura de 80%+
7. **Dockerizar** - Para deployment
8. **CI/CD** - GitHub Actions
