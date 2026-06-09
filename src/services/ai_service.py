from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from src.types.context_prestador import ContextPrestador, DadosPrestador, Endereco
from src.types.context_tomador import ContextTomador, DadosTomador, Tomador, Servico, Valores
from src.types.conversation_type import AIResponse
from src.types.incoming_msg import IncomingMessage
from src.models.prompts import AI_SYSTEM_PRESTADOR_GEMMA, AI_SYSTEM_ENDERECO_EXTRATOR_GEMMA, AI_SYSTEM_NF_GEMMA

load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_data_prestador(ctx: ContextPrestador) -> None:
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PRESTADOR_EXTRATOR},
                {"role": "user",   "content": ctx.text}
            ]
        )

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        ctx.dados_novos = DadosPrestador(
            razao_social=dados.get("razao_social"),
            cnpj=dados.get("cnpj"),
            email=dados.get("email"),
            regime_tributario=dados.get("regime_tributario"),
            cep=dados.get("cep"),
            inscricao_municipal=dados.get("inscricao_municipal")
        )
    except json.JSONDecodeError:
        print("Erro ao converter respota da ia para json")
        print(conteudo)
    
    except Exception as e:
        print("Erro ao analisar mensagem:", e)

def analisar_mensagem_ia(ctx) -> None:

    text = ctx.text
    conteudo = ""

    try:
        ai_system = AI_SYSTEM_CADASTRO
        
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
    
def analisar_msg_nota_ai(ctx: ContextTomador) -> None:

    text = ctx.text

    try:
        ai_system = AI_SYSTEM_EXTRACT_NF
        
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
        descricao = dados.get("servico", {}).get("descricao")
        total = dados.get("valores", {}).get("total")
        aliquotaIss = dados.get("valores", {}).get("aliquotaIss")

        ctx.dados_novos = DadosTomador(
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
    
def conversation_ativo_ai(history: list[dict], draft: dict) -> AIResponse:

    campos_presentes = _resumir_draft(draft)

    prompt = f"""
        Dados já coletados até agora:
        {campos_presentes}

        Continue a conversa com base no histórico acima.
        Extraia qualquer dado novo presente na última mensagem do usuário.
        Responda confirmando o que entendeu e pergunte o que ainda falta.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": AI_SYSTEM_CONVERSACIONAL},
                *history,
                {"role": "draft", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        conteudo = response.choices[0].message.content.strip()
        dados = json.loads(conteudo)

        return AIResponse(
            message=dados["message"],
            extraido=dados.get("extraido", {}),
        )
    
    except json.JSONDecodeError:
        return AIResponse(message="Desculpe, tive um problema interno. Pode repetir?", extraido={})
    
    except Exception as e:
        print("Erro ao analisar mensagem:", str(e))
        return AIResponse(message="Ocorreu um erro. Tente novamente.", extraido={})
    
def _resumir_draft(draft: dict) -> str:

    labels = {
        ("tomador", "nome"):      "Nome do tomador",
        ("tomador", "cnpj"):      "CNPJ",
        ("servico", "descricao"): "Descrição do serviço",
        ("valores", "total"):     "Valor total",
        ("valores", "aliquotaIss"): "Alíquota ISS",
    }

    rows = []

    for (secao, campo), label in labels.items():
        valor = draft.get(secao, {}).get(campo)
        rows.append(f"- {label}: {valor if valor is not None else 'nao informado'}")
    return "\n".join(rows)

# GEMMA

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


def extract_data_prestador_gemma(ctx: ContextPrestador) -> None:
    
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            temperature=0,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PRESTADOR_GEMMA},
                {"role": "user",   "content": ctx.text}
            ]
        )
        print(f"{response}\n")

        print(f"{response.choices[0].message.reasoning_content}\n")
        print(f"{response.choices[0].message.content}\n")

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        ctx.dados_novos = DadosPrestador(
            razao_social=dados.get("razao_social"),
            cnpj=dados.get("cnpj"),
            email=dados.get("email"),
            regime_tributario=dados.get("regime_tributario"),
            cep=dados.get("cep"),
            inscricao_municipal=dados.get("inscricao_municipal")
        )
    except json.JSONDecodeError:
        print("Erro ao converter respota da ia para json")
        print(conteudo)
    
    except Exception as e:
        print("Erro ao analisar mensagem:", e)

def extract_endereco_gemma(msg: IncomingMessage) -> Endereco:
    
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            temperature=0,
            messages=[
                {"role": "system", "content": AI_SYSTEM_ENDERECO_EXTRATOR_GEMMA},
                {"role": "user",   "content": msg.text}
            ]
        )

        print(f"{response}\n")
        print(f"{response.choices[0].message.reasoning_content}\n")
        print(f"{response.choices[0].message.content}\n")

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        return Endereco(
            logradouro=dados.get("logradouro"),
            numero=dados.get("numero"),
            bairro=dados.get("bairro"),
            cidade=dados.get("cidade"),
            uf=dados.get("uf"),
            cep=dados.get("cep"),
        )
    except json.JSONDecodeError:
        print("Erro ao converter respota da ia para json")
        print(conteudo)
    
    except Exception as e:
        print("Erro ao analisar mensagem:", e)

def extract_nf_gemma(ctx: ContextTomador) -> None:

    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            temperature=0,
            messages=[
                {"role": "system", "content": AI_SYSTEM_NF_GEMMA},
                {"role": "user", "content": ctx.text}
            ],
        )

        print(f"{response}\n")
        print(f"{response.choices[0].message.reasoning_content}\n")
        print(f"{response.choices[0].message.content}\n")

        conteudo = response.choices[0].message.content.strip()

        dados = json.loads(conteudo)

        nome = dados.get("tomador", {}).get("nome")
        cnpj = dados.get("tomador", {}).get("cnpj")
        descricao = dados.get("servico", {}).get("descricao")
        total = dados.get("valores", {}).get("total")
        aliquotaIss = dados.get("valores", {}).get("aliquotaIss")

        ctx.dados_novos = DadosTomador(
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