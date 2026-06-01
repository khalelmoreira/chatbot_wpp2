from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ============ Models para User ============

class UserBase(BaseModel):
    phone: str
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    status: str = "aguardando_dados"

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Models para Message ============

class MessageBase(BaseModel):
    user_phone: str
    message_id: str
    content: str
    message_type: str = "text"
    is_from_user: bool = True

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ Models para NFSe ============

class NFSeBase(BaseModel):
    user_phone: str
    tomador_nome: Optional[str] = None
    tomador_cnpj: Optional[str] = None
    servico_descricao: Optional[str] = None
    valor_total: Optional[float] = None
    status: str = "rascunho"

class NFSeCreate(NFSeBase):
    pass

class NFSeUpdate(BaseModel):
    tomador_nome: Optional[str] = None
    tomador_cnpj: Optional[str] = None
    servico_descricao: Optional[str] = None
    valor_total: Optional[float] = None
    status: Optional[str] = None

class NFSe(NFSeBase):
    id: int
    nfse_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Models para IA Analysis ============

class IAAnalysisResult(BaseModel):
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None

class IANFSeAnalysisResult(BaseModel):
    tomador: dict
    servico: dict
    valores: dict
