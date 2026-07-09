class NfNotFoundError(Exception):
    pass

class InvalidTransactionError(Exception):
    pass

class NtassOrgError(Exception):
    pass

class NtaasCertificadoError(NtassOrgError):
    pass

class CnpjJaCadastradoError(NtassOrgError):
    def __init__(self, existing_project_id: str):
        self.existing_project_id = existing_project_id
        super().__init__(f"CNPJ já cadastrado na organização: {existing_project_id}")

class LimitePlanoAtingidoError(NtassOrgError):
    pass

class DadosInvalidosError(NtassOrgError):
    def __init__(self, detalhe: str):
        self.detalhe = detalhe
        super().__init__(detalhe)