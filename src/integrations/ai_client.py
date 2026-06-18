import json
from abc import ABC, abstractmethod
from openai import OpenAI

class AIClient(ABC):
    """Interface para qualquer cliente de IA"""

    @abstractmethod
    def extract_json(self, system_prompt: str, user_msg: str) -> dict:
        """Extrai JSON da resposta da IA"""
        pass

    @abstractmethod
    def extract_text(self, system_prompt: str, user_msg: str) -> str:
        """Extrai texto da resposta da IA"""
        pass

class GemmaClient(AIClient):
    """Cliente para Gemma via LM-Studio"""

    def __init__(self, model: str, base_url: str = "http://localhost:1234/v1"):
        self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        self.model = model
        self.temperature = 0

    def extract_json(self, system_prompt: str, user_msg: str) -> dict:
        """Extrai e valida JSON"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            conteudo = response.choices[0].message.content.strip()
            return json.loads(conteudo)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Resposta inválida da IA. Esperado JSON válido: {e}")
        except Exception as e:
            raise Exception(f"Erro ao chamar IA: {e}")
        
    def extract_text(self, system_prompt: str, user_msg: str) -> str:
        """Extrai texto simples"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            print(f"EXTRACT_TEXT: {response.choices[0].message.content.split()}")
            return response.choices[0].message.content.split()
        except Exception as e:
            raise Exception(f"Erro ao chamar IA: {e}")