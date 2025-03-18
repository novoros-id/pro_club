from fastapi import APIRouter
from models import SimpleResponse
from config import settings
from deps import CurrenBot

router = APIRouter(prefix="/get", tags=["get"])

