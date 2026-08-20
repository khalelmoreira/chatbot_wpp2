"""Subconjunto verificado da lista nacional de serviços (LC 116/2003, cTribNac).

A lista completa tem ~200 subitens (40 grupos x subitens). Transcrever todos os
~200 a partir de buscas na web arriscaria erros silenciosos em dado fiscal —
por isso este arquivo só traz os códigos confirmados na própria documentação da
Notaas (https://docs.notaas.com.br/docs/codigos, verificado em 2026-08-19), a
plataforma de emissão já integrada neste projeto.

TODO: completar a lista com a tabela oficial completa (Portal Nacional da NFS-e /
gov.br/nfse) antes de depender disso para classificação em produção — hoje uma
descrição fora deste subconjunto sempre cai em UNCLASSIFIED, o que é seguro
(nunca "chuta" um código) mas limita a cobertura.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NationalServiceCode:
    codigo: str
    descricao: str


NATIONAL_SERVICE_CODES: tuple[NationalServiceCode, ...] = (
    NationalServiceCode("010700", "Suporte técnico em informática, incluindo instalação, configuração e manutenção"),
    NationalServiceCode("010601", "Consultoria e assessoria em informática"),
    NationalServiceCode("170601", "Propaganda e publicidade, promoção de vendas"),
    NationalServiceCode("090301", "Contabilidade, auditoria e congêneres"),
    NationalServiceCode("080101", "Ensino regular pré-escolar, fundamental, médio e superior"),
    NationalServiceCode("010302", "Armazenamento, hospedagem de dados, textos, imagens"),
)

UNCLASSIFIED = "UNCLASSIFIED"

_KNOWN_CODES: frozenset[str] = frozenset(c.codigo for c in NATIONAL_SERVICE_CODES)


def is_known_code(codigo: str) -> bool:
    return codigo in _KNOWN_CODES
