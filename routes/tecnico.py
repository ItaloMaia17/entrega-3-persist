from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Tecnico
from odmantic import ObjectId

router = APIRouter(
    prefix="/tecnicos",  # Prefixo referente a rota
    tags=["Tecnicos"],  # Tag para a documentação
)

# Motor
engine = get_engine()

# Rota para pegar todos os Tecnicos do banco
@router.get("/", response_model=list[Tecnico])
async def get_all_tecnicos(skip: int= 0, limit: int= 10) -> list[Tecnico]:
    list_tecnicos = await engine.find(Tecnico,skip=skip, limit=limit)
    return list_tecnicos

# Rota para pegar um tecnico por id
@router.get("/{tecnico_id}", response_model=Tecnico)
async def get_tecnico(tecnico_id: str) -> Tecnico:
    tecnico = await engine.find_one(Tecnico, Tecnico.id == ObjectId(tecnico_id))
    if not tecnico:
        raise HTTPException(status_code=404, detail="Tecnico não encontrado")
    return tecnico

# Rota para pegar técnico por nome
@router.get("/nome_tecnico/{nome_tec}", response_model=list[Tecnico])
async def list_tecnico_by_name(nome: str, skip: int= 0, limit: int= 10) -> list[Tecnico]:
    # Procura o técnico no banco
    list_tecnico = await engine.find(Tecnico, {"nome": {"$regex": nome, "$options":"i"}}, skip=skip, limit=limit)
    # Verifica se o técnico foi encontrado
    if not list_tecnico:
        raise HTTPException(status_code=404, detail="Nenhuma correspondência encontrada")

    return list_tecnico

# Rota para inserir um novo Tecnico no banco
@router.post("/", response_model=Tecnico)
async def create_tecnico(tecnico: Tecnico) -> Tecnico:
    # Verifica se já existe um tecnico com o mesmo nome
    existing_tecnico = await engine.find_one(Tecnico, Tecnico.nome == tecnico.nome)
    if existing_tecnico:
        raise HTTPException(status_code=400, detail="Tecnico já cadastrado")
    # Insere o tecnico no banco
    await engine.save(tecnico)
    return tecnico

# Rota para alterar dados de um Tecnico
@router.put("/{tecnico_id}", response_model=Tecnico)
async def update_tecnico(tecnico_id: str, tecnico_data: dict) -> Tecnico:
    # verifica se o tecnico esta no banco
    tecnico = await engine.find_one(Tecnico, Tecnico.id == ObjectId(tecnico_id))
    if not tecnico:
        raise HTTPException(status_code=404, detail="Tecnico não encontrado")
    # Substitui os campos que foram modificados
    for key, value in tecnico_data.items():
        setattr(tecnico, key, value)
    # Salva o tecnico atualizado
    await engine.save(tecnico)
    return tecnico

# Rota para deletar um tecnico
@router.delete("/{tecnico_id}")
async def delete_tecnico(tecnico_id: str) -> dict:
    tecnico = await engine.find_one(Tecnico, Tecnico.id == ObjectId(tecnico_id))
    if not tecnico:
        raise HTTPException(status_code=404, detail="Tecnico não encontrado")
    await engine.delete(tecnico)
    return {"msg": "Tecnico excluido com sucesso"}