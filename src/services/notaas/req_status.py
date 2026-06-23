import requests
from src.models import NOTAAS_BASE_URL
from src.types import StatusInvoice

def req_status_notaas(invoice_id: str, api_key: str) -> StatusInvoice:
    
    resp = requests.get(
        f"{NOTAAS_BASE_URL}/invoices/{invoice_id}/status",
        headers={"x-api-key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    return StatusInvoice(
        status=data["status"],
        ch_nfse=data.get("chNFSe"),
        n_nfse=data.get("nNFSe"),
        issued_at=data.get("issuedAt"),
        error_code=data.get("errorCode"),
        error_message=data.get("errorMessage"),
    )