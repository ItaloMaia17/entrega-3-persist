from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Servico, Peca, Dispositivo, Tecnico
from odmantic import ObjectId

router = APIRouter(
    prefix="/servicos",  # Prefixo referente a rota
    tags=["Servicos"],  # Tag para a documentação
)

# Motor
engine = get_engine()

# Rota para pegar todos os Servicos do banco
@router.get("/", response_model=list[Servico])
async def get_all_servicos() -> list[Servico]:
    list_servicos = await engine.find(Servico)
    return list_servicos

# Rota para pegar um servico por id
@router.get("/{servico_id}", response_model=Servico)
async def get_servico(servico_id: str) -> Servico:
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=404, detail="Servico não encontrado")
    return servico

# Rota para inserir um novo Servico no banco
@router.post("/", response_model=Servico)
async def create_servico(servico: Servico) -> Servico:
    # Verifica se já existe um servico do mesmo nome
    exist_servico = await engine.find_one(Servico, Servico.tipo_de_servico == servico.tipo_de_servico,
        Servico.descricao == servico.descricao)
    if exist_servico:
        raise HTTPException(status_code=400, detail="Servico já cadastrado")
    # Verifica se o dispositivo existe
    dispositivo= await engine.find_one(Dispositivo, Dispositivo.id == servico.dispositivo.id)
    if not dispositivo:
        raise HTTPException(status_code=400, detail="Dispositivo não encontrado")
    # Verifica se o tecnico existe  
    tecnico= await engine.find_one(Tecnico, Tecnico.id == servico.tecnico.id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Tecnico não encontrado")
    
    
    # Salva o servico no banco
    await engine.save(servico)
    return servico

# Rota para adicionar pecas a um servico
@router.post("/pecas_utilizadas", response_model=Servico)
async def add_peca_servico(servico_id: str, peca: Peca) -> Servico:
    # Verifica se já existe um servico do mesmo nome
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=400, detail="servico não encontrado")
    # Atualiza o servico no banco
    servico.pecas_ids.append(peca.id)
    await engine.save(servico)
    return servico

# Rota para alterar dados de um Servico
@router.put("/{servico_id}", response_model=Servico)
async def update_servico(servico_id: str, servico_data: dict) -> Servico:
    # verifica se o servico esta no banco
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=404, detail="Servico não encontrado")
    # Substitui os campos que foram modificados
    for key, value in servico_data.items():
        setattr(servico, key, value)
    # Salva o servico atualizado
    await engine.save(servico)
    return servico

# Rota para deletar um servico
@router.delete("/{servico_id}")
async def delete_servico(servico_id: str) -> dict:
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=404, detail="Servico não encontrado")
    await engine.delete(servico)
    return {"msg": "Servico excluido com sucesso"}