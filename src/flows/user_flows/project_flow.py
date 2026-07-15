import os
import logging
from src.types import ContextPrestador, CnpjJaCadastradoError, LimitePlanoAtingidoError, DadosInvalidosError, UserStatus
from src.services.sign_up.project_service import ProjectService
from src.managers.user_manager import PrestadorManager

logger = logging.getLogger(__name__)

def project_flow(ctx: ContextPrestador):
        
    print(f"\n\n----------------PROJECT FLOW----------------\n\n")
    
    prestador = PrestadorManager(ctx)
    nts = ProjectService(ctx)

    try:
        project_id = nts.create_project(os.environ["NTAAS_ORG_TOKEN"])

    except CnpjJaCadastradoError as e:
        project_id = e.existing_project_id
    
    except (LimitePlanoAtingidoError, DadosInvalidosError) as e:
        prestador.update_error(UserStatus.ERROR, str(e))
        raise

    prestador.update_project_id(project_id, UserStatus.CERTIFICATE)