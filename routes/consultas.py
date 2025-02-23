from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Dispositivo, Tecnico, Peca, Servico

router = APIRouter(
    prefix="/consultas",
    tags=["Consultas"]
)
# Motor
engine = get_engine()




