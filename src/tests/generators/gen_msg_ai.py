from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gen_msg_fake(tipo: str = "nsfe", quantidade: int = 3) -> list[str]:
    
    ai_system = """
    You are a Brazilian customer message simulator for software testing purposes.

    Your task is to generate realistic fictional messages that Brazilian customers might send via WhatsApp, SMS, or chat — either to request a NFS-e (Nota Fiscal de Serviços Eletrônica) or to provide registration data (nome, CPF/CNPJ, email).

    CRITICAL — WRITING STYLE:
    Messages must sound like a real person typing on a phone. They must NEVER look like a form or a structured list.

    FORBIDDEN patterns (too structured — never generate these):
    - "nome: João Silva, cpf: 123.456.789-00"
    - "Segue os dados: empresa ACME, CNPJ 12.345.678/0001-99, email: joao@acme.com"
    - "Dados para nota: tomador: João, valor: R$ 500,00, alíquota: 2%"

    CORRECT patterns (natural, conversational — always generate like these):
    - "bom dia minha empresa é a Tech Solutions ME o cnpj 11222333000181 e o email é contato@techsolutions.com.br"
    - "nao sei a aliquota mas é pra Construtora Boa Vista cnpj 44555666000177 consult de eng valor 8500"
    - "opa, preciso emitir nota. empresa logistica rapida. cnpj esqueci aqui mas o email é financeiro@lograp.com.br"
    - "emite nota pra ACME Serviços LTDA cnpj 12345678000199 manutencao predial dois mil reais iss 3 porcento"
    - "oi preciso cadastrar minha empresa Soluções Digitais ME cnpj 98765432000100 email contato@soldig.com.br"

    The data must flow naturally inside the sentence — never as labeled fields or bullet points.

    NFS-e SPECIFIC RULES:
    * NFS-e messages must reference ONLY companies (razão social) as the recipient — never individual persons
    * NFS-e messages must include CNPJ when a fiscal number is provided — never CPF
    * If the message mentions a recipient without a CNPJ, that is acceptable (missing field scenario)

    CADASTRO SPECIFIC RULES:
    * Registration messages may reference either a person or a company
    * May include CPF (for individuals) or CNPJ (for companies)

    VARIATION RULES:
    * Mix formal and informal register across messages
    * Use abbreviations and slang: "vc", "tb", "pra", "q", "eh", "nao" (sem acento), "to", "tá"
    * Include spelling mistakes and typos in some messages
    * Vary punctuation: some messages with none, some with excess, some normal
    * Include regional filler words: "então", "tipo", "né", "ó", "olha"
    * Some messages should have missing fields — that is expected and realistic
    * CNPJ formats must vary: with dots and slashes, digits only, partially formatted
    * Monetary values: "500 reais", "quinhentos", "R$500", "R$ 500,00", "500,00"

    HARD RULES:
    * Generate ONLY the message text — no labels, no JSON keys, no metadata
    * Never use real CPF or CNPJ numbers
    * All personal data must be entirely fictional
    * Each message must differ in structure, tone, length, and content
    * Never repeat sentence-opening patterns across messages in the same batch
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": ai_system},
            {"role": "user", "content": build_prompt(tipo, quantidade)}
        ],
        temperature=0.7
    )
    conteudo = response.choices[0].message.content.strip()
    return json.loads(conteudo)
        
def build_prompt(tipo: str, quantidade: int) -> str:
    tipos = {
        "cadastro": (
            "registration messages where the customer provides their name or company name, "
            "CPF (if individual) or CNPJ (if company), and email — as if typing to create an account"
        ),
        "nfse": (
            "NFS-e request messages where the customer provides the recipient company name (razão social), "
            "CNPJ (never CPF — NFS-e is issued only for companies), "
            "service description, total value, and ISS aliquot"
        ),
        "misto": (
            "a mix of registration messages and NFS-e requests — "
            "roughly half of each type"
        ),
    }

    descricao = tipos.get(tipo, tipos["misto"])

    cenarios_nfse = """
    - All fields present (company name + CNPJ + service + value + aliquot), data well-formatted
    - All fields present, CNPJ with missing or wrong punctuation
    - Company name present but CNPJ missing
    - CNPJ present but company name missing
    - Value and aliquot missing
    - Very short message (company name and service only)
    - Very long and rambling message with filler words
    - Heavy use of abbreviations and slang
    - Obvious spelling mistakes in company name or service
    - Aliquot or value written out in words (ex: "dois porcento", "mil e duzentos reais")
    """

    cenarios_cadastro = """
    - All fields present (name + CPF or CNPJ + email), data well-formatted
    - All fields present, CPF/CNPJ poorly formatted
    - Email in uppercase or with extra spaces
    - Name present but fiscal number missing
    - Very short message (name only)
    - Ambiguous message where it is unclear if it is a person or a company
    - Obvious spelling mistakes
    - Heavy use of abbreviations and slang
    - Email missing, only name and fiscal number
    """

    cenarios_misto = cenarios_nfse + cenarios_cadastro

    cenarios = {
        "nfse": cenarios_nfse,
        "cadastro": cenarios_cadastro,
        "misto": cenarios_misto,
    }.get(tipo, cenarios_misto)

    return f"""Generate {quantidade} fictional Brazilian customer messages for testing purposes.

    Message type: {descricao}

    Distribute these scenarios across the {quantidade} messages — each must represent a different case:
    {cenarios}

    REMINDER: data must appear naturally inside the sentence — never as "campo: valor" or comma-separated labeled lists.

    Return ONLY a JSON array of strings. No markdown, no explanations, no labels.
    Format: ["mensagem 1", "mensagem 2", "mensagem 3"]
    """

def gen_conversa_fake(
    tipo: str = "nfse",
    num_conversas: int = 3,
    turnos_conversa: tuple[int, int] = (2, 4),  # min, max turnos
) -> list[list[str]]:
    """
    Gera conversas multi-turno onde o cliente fragmenta os dados ao longo
    de várias mensagens, simulando acúmulo de contexto.

    Retorna: lista de conversas, cada conversa é uma lista de mensagens ordenadas.
    Exemplo:
        [
            ["emite nota pra mim", "é pra Tech Solutions", "cnpj 11222333000181 valor 500"],
            ["preciso de uma nfse", "serviço de consultoria dois mil reais", "cnpj 44555666000177 iss 3%"],
        ]
    """

    ai_system = """
    You are a Brazilian customer conversation simulator for software testing purposes.

    Your task is to generate realistic multi-turn WhatsApp/chat conversation sequences.
    Each sequence represents ONE customer making ONE request, but spreading the information
    across MULTIPLE messages — exactly as people do in real messaging apps.

    CORE CONCEPT — FRAGMENTED INFORMATION:
    The customer does NOT send all data in one message. They break it up naturally:
    - First message: vague intent or partial info ("emite nota pra mim")
    - Middle messages: additional fields provided as remembered ("ah o cnpj é...")
    - Last message: remaining info, confirmation, or correction

    REALISTIC FRAGMENTATION PATTERNS:
    - Intent first, then details: "preciso de nota" → "é pra ACME Ltda" → "cnpj 12345678000199 valor 800"
    - Partial data, then complement: "nota pra Tech Solutions cnpj 111" → "o cnpj completo é 11122233000144" → "valor 1500 iss 2%"
    - Interruption and return: "oi, nota fiscal" → "pera" → "ok, empresa Logística Boa Vista, serviço de frete"
    - Correction mid-conversation: "valor é 500" → "na verdade são 550 reais"
    - Forgot something: "cnpj 44555666000177" → "esqueci, o serviço é manutenção predial"
    - Confirms before finishing: "tá certo assim?" → "o cnpj é 99888777000155"

    WRITING STYLE — same rules as isolated messages:
    * Natural phone typing — never structured like a form
    * Mix formal/informal, abbreviations, typos, filler words
    * Each message in a sequence should feel like a real follow-up, not a list item

    SEQUENCE COHERENCE RULES:
    * All messages in a sequence must refer to the SAME request
    * Information must NOT be repeated unnecessarily between turns
    * Later messages may correct or complement earlier ones
    * Some sequences may end with missing fields (incomplete request — that is valid)

    NFS-e RULES:
    * Recipient is always a company (razão social) — never an individual
    * Fiscal number is always CNPJ — never CPF

    HARD RULES:
    * Generate ONLY message text — no labels, no metadata
    * All data must be entirely fictional
    * Never use real CPF or CNPJ numbers
    * Each sequence must differ in structure, tone, and fragmentation pattern
    """

    prompt = build_prompt_conversa(tipo, num_conversas, turnos_conversa)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=3000,
        messages=[
            {"role": "system", "content": ai_system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )

    conteudo = response.choices[0].message.content.strip()
    return json.loads(conteudo)

def build_prompt_conversa(
    tipo: str,
    num_conversas: int,
    turnos_conversa: tuple[int, int],
) -> str:
    tipos = {
        "nfse": (
            "NFS-e request sequences — customer provides recipient company (razão social), "
            "CNPJ, service description, total value, and ISS aliquot across multiple messages"
        ),
        "cadastro": (
            "registration sequences — customer provides name or company, "
            "CPF or CNPJ, and email across multiple messages"
        ),
        "misto": (
            "a mix — roughly half NFS-e requests and half registration sequences"
        ),
    }

    descricao = tipos.get(tipo, tipos["misto"])
    min_t, max_t = turnos_conversa

    cenarios = """
    Distribute these fragmentation scenarios across the sequences:
    - Intent only in first message, all data spread across remaining turns
    - First message has half the data, second has the rest
    - Customer sends CNPJ in one message, company name in another (out of "expected" order)
    - Customer corrects a value or name in a later turn
    - Customer forgets a field and sends it as the last message ("esqueci, o iss é 2%")
    - Very short turns (2 messages total), one vague + one with everything else
    - Customer pauses mid-conversation with filler ("pera aí", "um segundo")
    - Sequence ends incomplete — one or two fields never provided
    - Customer sends a confirmation question in one turn ("é assim mesmo?")
    - Heavy slang and abbreviations distributed across turns
    """

    return f"""Generate {num_conversas} multi-turn conversation sequences for testing purposes.

    Request type: {descricao}

    Each sequence must have between {min_t} and {max_t} messages.
    {cenarios}

    Return ONLY a JSON array of arrays of strings. No markdown, no explanations.
    Format:
    [
        ["primeira mensagem da conversa 1", "segunda mensagem", "terceira mensagem"],
        ["primeira mensagem da conversa 2", "segunda mensagem"],
        ...
    ]"""

if __name__ == '__main__':
    conversas = gen_conversa_fake(
        tipo="nfse",
        num_conversas=1,
        turnos_conversa=(2, 4)
    )
    for i, conversa in enumerate(conversas):
        print(conversa)