from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Dispositivo
from odmantic import ObjectId

router = APIRouter(
    prefix="/dispositivos", # Prefixo referente a rota
    tags=["Dispositivos"], # Tag para a documentação
)

# Motor
engine = get_engine()

# Rota para pegar todos os Dispositivos do banco
@router.get("/dispositivos/", response_model= list[Dispositivo])
async def get_all_disp()-> list[Dispositivo]:
    list_disp = await engine.find(Dispositivo)
    return list_disp

# Rota para pegar um dispositivo por id
@router.get("/dispositivos/{disp_id}", response_model= Dispositivo)
async def get_disp(disp_id: str)-> Dispositivo:
    disp = await engine.find_one(Dispositivo, Dispositivo.id == ObjectId(disp_id))
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    return disp

# Rota para inserir um novo Dispositivo no banco
@router.post("/dispositivos/", response_model= Dispositivo)
async def create_disp(dispositivo: Dispositivo)-> Dispositivo:
    # Verifica se já existe um dispositivo do mesmo modelo
    disp = await engine.find_one(Dispositivo, Dispositivo.modelo == dispositivo.modelo)
    if disp:
        raise HTTPException(status_code=400, detail="Dispositivo já cadastrado")
    # Insere o dispositivo no banco
    await engine.save(dispositivo)
    return dispositivo


# Rota para alterar dados de um Dispositivo
@router.put("/dispositivos/", response_model=Dispositivo)
async def update_disp(disp_id: str, disp_data: dict)-> Dispositivo:
    # verifica se o dispositivo esta no banco
    disp = await engine.find_one(Dispositivo, Dispositivo.id == ObjectId(disp_id))
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    # Substitui os campos que foram modificados
    for key, value in disp_data.items():
        setattr(disp, key, value)
    # Salva o dispositivo atualizado
    await engine.save(disp)
    return disp

# Rota para deletar um dispositivo
@router.delete("/dispositivos/{disp_id}")
async def delete_disp(disp_id: str)-> dict:
    disp= await engine.find_one(Dispositivo, Dispositivo.id == ObjectId(disp_id))
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    await engine.delete(disp)
    return {"msg": "Dispositivo excluido com sucesso"}

