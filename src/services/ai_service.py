from openai import OpenAI
import json
import os
import re
from dotenv import load_dotenv
from src.types.context_cadastro import ContextCadastro, DadosCadastro
from src.types.context_nfse import ContextNfse, DadosNfse, Tomador, Servico, Valores

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analisar_mensagem_ia(ctx: ContextCadastro) -> None:

    text = ctx.text
    conteudo = ""

    try:
        ai_system = """
    You are a specialized AI system for extracting structured registration data from Brazilian customer messages.

    The user messages will always be in Brazilian Portuguese and may be informal, abbreviated, or contain spelling mistakes.

    Your task is to extract ONLY the fields listed below and return them as valid JSON.

    OUTPUT FORMAT:
    You must ALWAYS return ONLY valid JSON with this EXACT structure:

    {
        "nome": string or null,
        "cpf_cnpj": string or null,
        "email": string or null
    }

    GENERAL RULES:
    * Respond ONLY with valid JSON — no explanations, comments, or markdown
    * Never invent or assume missing data; use null for absent fields
    * Never create fields outside the defined schema
    * If the message contains more than one value for the same field, extract only the first one mentioned

    FIELD NORMALIZATION RULES:

    nome:
    * Preserve the original capitalization as provided by the user
    * If the name is fully uppercase or fully lowercase in the message, keep it as-is
    * Examples:
    - "meu nome é joao silva" → "joao silva"
    - "empresa ACME LTDA" → "ACME LTDA"

    cpf_cnpj:
    * Remove all non-digit characters (dots, slashes, dashes)
    * CPF must have 11 digits; CNPJ must have 14 digits
    * If the extracted value does not match either length, return null
    * Examples:
    - "123.456.789-00" → "12345678900"
    - "12.345.678/0001-99" → "12345678000199"

    email:
    * Return in lowercase and trimmed
    * Only return a value if it matches a valid email format (contains "@" and a domain)
    * If the email appears malformed or incomplete, return null
    * Examples:
    - "JOAO@GMAIL.COM" → "joao@gmail.com"
    - "joao gmail com" → null

    EXAMPLES:

    Input: "meu nome é joao silva cpf 123.456.789-00 email JOAO@GMAIL.COM"
    Output:
    {
        "nome": "joao silva",
        "cpf_cnpj": "12345678900",
        "email": "joao@gmail.com"
    }

    Input: "empresa ACME LTDA, cnpj 12.345.678/0001-99, contato financeiro@acme.com"
    Output:
    {
        "nome": "ACME LTDA",
        "cpf_cnpj": "12345678000199",
        "email": "financeiro@acme.com"
    }

    Input: "joao da silva"
    Output:
    {
        "nome": "joao da silva",
        "cpf_cnpj": null,
        "email": null
    }
    """
        
        prompt = f"""
        Extract structured data from the following customer message.

        Return only valid JSON.

        Message:
        \"\"\"{text}\"\"\"
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": ai_system},
                
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        nome = dados.get("nome")
        cpf_cnpj = dados.get("cpf_cnpj")
        email = dados.get("email")

        print(f"nome: {nome}\n")
        print(f"cpf_cnpj: {cpf_cnpj}\n")
        print(f"email: {email}\n")

        ctx.dados_novos = DadosCadastro(
            nome=dados.get("nome"),
            cpf_cnpj=dados.get("cpf_cnpj"),
            email=dados.get("email")
        )
    
    except json.JSONDecodeError:
        print("Erro ao converter respota da ia para json")
        print(conteudo)
    
    except Exception as e:
        print("Erro ao analisar mensagem:", e)
    
def analisar_msg_nota_ai(ctx: ContextNfse) -> None:

    text = ctx.text

    try:
        ai_system = """
    You are a specialized AI system for extracting structured fiscal data from Brazilian customer messages for NFS-e (Nota Fiscal de Serviços Eletrônica) issuance.

    The user messages will always be in Brazilian Portuguese and may be informal, abbreviated, or contain spelling mistakes.

    Your task is to extract ONLY the essential data required for NFS-e issuance and return it as valid JSON.

    OUTPUT FORMAT:
    You must ALWAYS return ONLY valid JSON with this EXACT structure:

    {
        "tomador": {
            "nome": string or null,
            "cnpj": string or null
        },
        "servico": {
            "descricao": string or null
        },
        "valores": {
            "total": number or null,
            "aliquotaIss": number or null
        }
    }

    GENERAL RULES:
    * Respond ONLY with valid JSON — no explanations, comments, or markdown
    * Never invent or assume missing data; use null for absent fields
    * Never create fields outside the defined schema
    * Extract data even from informal, abbreviated, or misspelled messages
    * If the message mentions more than one recipient or service, extract only the first one mentioned
    * Preserve the original meaning of the service description

    FIELD NORMALIZATION RULES:

    nome:
    * Accept ONLY company names (razão social) — e.g. "ACME LTDA", "Tech Solutions ME"
    * If the recipient is a person (individual), return null
    * Preserve the original capitalization as provided by the user

    cnpj:
    * Accept ONLY CNPJ (14 digits) — if a CPF (11 digits) is provided, return null
    * Remove all non-digit characters (dots, slashes, dashes)
    * If the extracted value does not have exactly 14 digits, return null
    * Examples:
    - "12.345.678/0001-99" → "12345678000199"
    - "123.456.789-00" (CPF) → null

    Monetary values (total):
    * Always return as a number (float or integer), never as a string
    * Handle Brazilian formatting: period as thousand separator, comma as decimal
    * Examples:
    - "150 reais" → 150
    - "89,90" → 89.90
    - "R$ 1.500,00" → 1500.00

    ISS aliquot (aliquotaIss):
    * Always return as a number without the percent symbol
    * Examples:
    - "2%" → 2
    - "5 porcento" → 5
    - "dois por cento" → 2
    - "2 %" → 2

    Service description (descricao):
    * Should be concise and directly describe the informed service
    * Return in lowercase unless proper nouns are present
    * Examples:
    - "serviço de manutenção de ar condicionado" → "manutenção de ar condicionado"
    - "desenvolvimento de software" → "desenvolvimento de software"

    EXAMPLES:

    Input: "emitir nota para ACME LTDA cnpj 12.345.678/0001-99 serviço de manutenção valor 150 reais aliquota 2%"
    Output:
    {
        "tomador": {
            "nome": "ACME LTDA",
            "cnpj": "12345678000199"
        },
        "servico": {
            "descricao": "manutenção"
        },
        "valores": {
            "total": 150,
            "aliquotaIss": 2
        }
    }

    Input: "nota para joao silva cpf 123.456.789-00 serviço de desenvolvimento"
    Output:
    {
        "tomador": {
            "nome": null,
            "cnpj": null
        },
        "servico": {
            "descricao": "desenvolvimento"
        },
        "valores": {
            "total": null,
            "aliquotaIss": null
        }
    }

    Input: "nota pra Tech Solutions ME cnpj 44.555.666/0001-77 consultoria R$ 1.500,00 iss 2 %"
    Output:
    {
        "tomador": {
            "nome": "Tech Solutions ME",
            "cnpj": "44555666000177"
        },
        "servico": {
            "descricao": "consultoria"
        },
        "valores": {
            "total": 1500.00,
            "aliquotaIss": 2
        }
    }
    """
        
        prompt = f"""
        Extract structured fiscal data from the following customer message.

        Return ONLY valid JSON.

        Customer message:
        \"\"\"{text}\"\"\"
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": ai_system},
                
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        nome = dados.get("tomador", {}).get("nome")
        cnpj = dados.get("tomador", {}).get("cnpj")

        print(f"nome: {nome}\n")
        print(f"cnpj: {cnpj}\n")

        descricao = dados.get("servico", {}).get("descricao")

        print(f"descricao: {descricao}\n")

        total = dados.get("valores", {}).get("total")
        aliquotaIss = dados.get("valores", {}).get("aliquotaIss")

        print(f"total: {total}\n")
        print(f"aliquota: {aliquotaIss}\n")

        ctx.dados_novos = DadosNfse(
            tomador=Tomador(
                nome=nome,
                cnpj=cnpj
            ),
            servico=Servico(
                descricao=descricao
            ),
            valores=Valores(
                total=total,
                aliquotaIss=aliquotaIss
            )
        )

    except json.JSONDecodeError:
        print("Erro ao converter respota da ia para json")
        print(conteudo)
        return
    
    except Exception as e:
        print("Erro ao analisar mensagem:", str(e))
        return