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

class IssResolutionError(Exception):
    """Código classificado não tem alíquota vigente na tabela local — falha visível,
    nunca um valor default/zero silencioso."""

class IssRateSyncError(Exception):
    """Resposta da API de Parâmetros Municipais (ADN) veio em formato inesperado —
    melhor falhar alto do que tentar adivinhar o shape."""

class NotaasEmissaoError(Exception):
    """Notaas recusou ou falhou ao processar uma emissão de NFS-e."""

class NotaasEmissaoPermanenteError(NotaasEmissaoError):
    """Notaas rejeitou o payload (4xx) — dado do payload está errado, tentar de
    novo sem mudar nada só repete o mesmo erro. Não deve ser reenfileirado."""

class NotaasEmissaoTransitoriaError(NotaasEmissaoError):
    """Falha de rede, timeout ou erro 5xx da Notaas — pode ser uma instabilidade
    passageira (ex.: prefeitura fora do ar). Segue elegível para retry com backoff."""