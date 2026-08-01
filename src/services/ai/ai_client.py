import json
from src.types import AIClient
from openai import OpenAI

class GemmaClient(AIClient):

    def __init__(self, model: str = "google/gemma-4-e4b", base_url: str = "http://localhost:1234/v1"):
        self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        self.model = model
        self.temperature = 0

    def extract_json(self, system_prompt: str, user_msg: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            conteudo = response.choices[0].message.content
            if conteudo is None:
                return {}
            return json.loads(conteudo.strip())
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Resposta inválida da IA. Esperado JSON válido: {e}")
        except Exception as e:
            raise Exception(f"Erro ao chamar IA: {e}")
        
    def extract_text(self, system_prompt: str, user_msg: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            conteudo = response.choices[0].message.content
            if conteudo is None:
                return ""
            return conteudo
        except Exception as e:
            raise Exception(f"Erro ao chamar IA: {e}")