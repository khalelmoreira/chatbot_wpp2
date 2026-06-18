from dataclasses import dataclass
from typing import Optional

@dataclass
class AIPrompt:
    name: str
    model: str
    system: str                  # Instruções do sistema
    version: str = "1.0"         # Versionamento
    description: str = ""        # Documentação

    def __str__(self) -> str:
        return self.system
    
@dataclass
class ToolSchema:
    """Schema de ferramenta para IA"""
    name: str
    description: str
    input_schema: dict