from fastapi import APIRouter, Depends
from app.deps import get_db_provider
from app.core.provider_db import Provider
from app.models import CreateProgramConnection 
from app.services.program_settings_service import ProgramSettingsService

program_settings_service = ProgramSettingsService()

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/")
async def read_root():
    return {"message": "root settings"} 

@router.post("/connection_settings")
async def create_user(create_program: CreateProgramConnection, db_provider: Provider = Depends(get_db_provider)):
    return await program_settings_service.upsert_connection_settings(create_program, db_provider)