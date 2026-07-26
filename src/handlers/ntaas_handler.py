from src.services.ntaas.ntaas_parser_service import NtaasParser

def processar_webhook_notaas(payload_raw):

    nt = NtaasParser(payload_raw)
    payload = nt.parse()
    return nt.dispatch(payload=payload)