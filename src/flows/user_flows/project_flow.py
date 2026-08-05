import os
import logging
from src.types import (
    ContextPrestador, CnpjJaCadastradoError, LimitePlanoAtingidoError, DadosInvalidosError,
    NtassOrgError, UserStatus, PrestadorData, InvalidTransactionError,
)
from src.services.sign_up.project_service import ProjectService
from src.managers.user_manager import PrestadorManager
from src.flows.user_flows.certificate_flow import cerfiticate_flow

logger = logging.getLogger(__name__)

def project_flow(ctx: ContextPrestador):

    print(f"\n\n----------------PROJECT FLOW----------------\n\n")

    prestador = PrestadorManager(ctx)

    dados = prestador.get_db_data()
    if dados is None:
        raise InvalidTransactionError(f"Prestador id={ctx.user.id} não encontrado ao iniciar project_flow")

    ctx.valid = PrestadorData.from_prestador(dados)
    nts = ProjectService(ctx)

    try:
        project_id = nts.create_project(os.environ["NTAAS_ORG_TOKEN"])

    except CnpjJaCadastradoError as e:
        project_id = e.existing_project_id

    except (LimitePlanoAtingidoError, DadosInvalidosError) as e:
        prestador.update_error(UserStatus.ERROR, str(e))
        raise

    if project_id is None:
        prestador.update_error(UserStatus.ERROR, "Notaas não retornou um project_id.")
        raise NtassOrgError("Notaas retornou status inesperado ao criar projeto.")

    prestador.update_project_id(project_id, UserStatus.CERTIFICATE)
    return cerfiticate_flow(ctx)
