
from app.models import CreateProgramConnection, ProgramConnectionBase
import app.utils.response as response_utils
from app.core.provider_db import Provider

class ProgramSettingsService:
    def __init__(self):
        pass

    async def upsert_connection_settings(self, 
                                         program_connection: CreateProgramConnection, 
                                         db_provider: Provider) -> ProgramConnectionBase:
        program = db_provider.upsert_connection_settings(program_connection)
        response_text = f'Настройки подключения {program.name} успешно сохранены!'
        simple_response = response_utils.create_simple_response_from_request(program_connection, response_text)
        response = await response_utils.send_request(simple_response, "upsert_connection_settings", db_provider)
        return program