from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Servico, Peca, Dispositivo, Tecnico
from pymongo import ASCENDING, DESCENDING
from odmantic import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/servicos",  # Prefixo referente a rota
    tags=["Servicos"],  # Tag para a documentação
)

# Motor
engine = get_engine()

# Rota para pegar todos os Servicos do banco
@router.get("/", response_model=list[Servico])
async def get_all_servicos(skip: int= 0, limit: int= 10) -> list[Servico]:
    list_servicos = await engine.find(Servico, skip=skip, limit=limit)
    return list_servicos

# Rota para pegar um servico por id
@router.get("/{servico_id}", response_model=Servico)
async def get_servico(servico_id: str) -> Servico:
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=404, detail="Servico não encontrado")
    return servico

# Rota para pegar serviços por tipo
@router.get("/tipo/{tipo_servico}", response_model=list[Servico])
async def list_servicos_by_type(tipo_servico: str, skip: int= 0, limit: int= 10) -> list[Servico]:
    # Procura o serviço no banco
    servicos = await engine.find(Servico, {"tipo_servico": {"$regex": tipo_servico, "$options":"i"}}, skip=skip, limit=limit)
    # Verifica se o serviço foi encontrado
    if not servicos:
        raise HTTPException(status_code=404, detail="Nenhuma correspondência encontrada")

    return servicos

# Rota para pegar um Serviço pelo Técnico
@router.get("/tecnico/{tecnico_id}", response_model=list[Servico])
async def list_servicos_by_tecnico(tecnico_id: str, skip: int= 0, limit: int= 10) -> list[Servico]:
    # Procura o serviço no banco
    servicos = await engine.find(Servico, Servico.tecnico == ObjectId(tecnico_id), skip=skip, limit=limit)
    # Verifica se o serviço foi encontrado
    if not servicos:
        raise HTTPException(status_code=404, detail="Nenhuma correspondência encontrada")

    return servicos

# Rota para pegar todos os serviços associados a um dispositivo
@router.get("/dispositivo/{dispositivo_id}", response_model=list[Servico])
async def list_servicos_by_dispositivo(dispositivo_id: str, skip: int= 0, limit: int= 10) -> list[Servico]:
    # Procura o serviço no banco
    servicos = await engine.find(Servico, Servico.dispositivo == ObjectId(dispositivo_id), skip=skip, limit=limit)
    # Verifica se o serviço foi encontrado
    if not servicos:
        raise HTTPException(status_code=404, detail="Nenhuma correspondência encontrada")
    return servicos

# Rota para pegar pegar os serviços cadastrados em um determinado intervalo de tempo
@router.get("/ano/{ano}", response_model=list[Servico])
async def list_servicos_by_year(ano: int, skip: int= 0, limit: int= 10) -> list[Servico]:
    ano_inico= datetime(ano,1,1)
    ano_fim= datetime(ano+1,1,1)
    # Procura o serviço no banco
    servicos = await engine.find(Servico,{"cadastrado_em": {"$gte":ano_inico, "$lt": ano_fim}}, skip=skip, limit=limit)
    # Verifica se o serviço foi encontrado
    if not servicos:
        raise HTTPException(status_code=404, detail="Nenhuma correspondência encontrada")

    return servicos

# Rota para media do valor dos serviços cada tecnico(consulta com agregação e média)
@router.get("/media_valor_tecnico/", response_model=dict)
async def media_valor_tecnico(id_tecnico: str) -> dict:
    # verifica se existe algum serviço atribuido ao tecnico
    exist_tecnico= await engine.find(Servico, Servico.tecnico== ObjectId(id_tecnico))
    if not exist_tecnico:
        raise HTTPException(status_code=404, detail="Nenhum serviço atribuido a esse Técnico")
    # Acessar a coleção diretamente
    database = engine.client["assistencia"]
    collection = database["servico"]

    pipeline = [
        {"$match": {"tecnico": ObjectId(id_tecnico)}},
        {"$group": {"_id": "$tecnico", "media_valor_servico": {"$avg": "$valor"}}},
        {"$lookup": {"from": "tecnico", "localField": "_id", "foreignField": "_id", "as": "tecnico_info"}},
        {"$unwind": "$tecnico_info"},
        {"$project": {
            "_id": 0, 
            "nome_tecnico": "$tecnico_info.nome", 
            "especialidade": "$tecnico_info.especialidade", 
            "media_valor_servico": 1}
            }
    ]

    media_valor_servico = await collection.aggregate(pipeline).to_list(length=1)
    if not media_valor_servico:
        raise HTTPException(status_code=404, detail="Não existem serviços atribuidos a esse técnico")
    return media_valor_servico[0]

# Ordenar os Serviços por valor(ordenação com agregação)
@router.get("/ordenar_valor/", response_model=list[Servico])
async def order_servicos_by_value(order:int=1, skip:int=0, limit:int=10) -> list[Servico]:
    # Especifica a ordem da ordenação
    service_order = 1 if order == 1 else -1
    # Acessa a coleção diretamente
    database = engine.client["assistencia"]
    collection = database["servico"]

    pipeline = [
        {"$sort": {"valor": service_order}},
        {"$skip": skip},
        {"$limit": limit},
        {"$lookup": {"from": "tecnico", "localField": "tecnico", "foreignField": "_id", "as": "tecnico_info"}},
        {"$unwind": "$tecnico_info"},
        {"$lookup": { "from": "dispositivo", "localField": "dispositivo", "foreignField": "_id","as": "dispositivo_info"}},
        {"$unwind": "$dispositivo_info"},
        {"$project": {
            "_id": 0,
            "tipo_servico": 1,
            "descricao": 1,
            "dispositivo": "$dispositivo_info",
            "valor": 1,
            "tecnico": "$tecnico_info",
            "pecas_ass":1
        }}
    ]

    servicos = await collection.aggregate(pipeline).to_list(length=limit)
    return servicos


# Rota para inserir um novo Servico no banco
@router.post("/", response_model=Servico)
async def create_servico(servico: Servico) -> Servico:
    # Verifica se já existe um servico do mesmo nome
    exist_servico = await engine.find_one(Servico, Servico.tipo_servico == servico.tipo_servico,
        Servico.descricao == servico.descricao)
    if exist_servico:
        raise HTTPException(status_code=400, detail="Servico já cadastrado")
    # Verifica se o dispositivo existe
    dispositivo= await engine.find_one(Dispositivo, Dispositivo.modelo == servico.dispositivo.modelo)
    if not dispositivo:
        raise HTTPException(status_code=400, detail="Dispositivo não encontrado")
    # Verifica se o tecnico existe  
    tecnico= await engine.find_one(Tecnico, Tecnico.nome == servico.tecnico.nome)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Tecnico não encontrado")
    
    servico.dispositivo= dispositivo
    servico.tecnico=tecnico
    # Salva o servico no banco
    await engine.save(servico)
    return servico

# Rota para adicionar pecas a um servico
@router.post("/pecas_utilizadas/", response_model=Servico)
async def add_peca_servico(servico_id: str, peca: Peca) -> Servico:
    # Verifica se já existe um servico do mesmo nome
    servico = await engine.find_one(Servico, Servico.id == ObjectId(servico_id))
    if not servico:
        raise HTTPException(status_code=400, detail="servico não encontrado")
    # Verifica se a peça existe
    peca= await engine.find_one(Peca, Peca.nome == peca.nome)
    if not peca:
        raise HTTPException(status_code=400, detail="Peça não encontrada")
    # Atualiza o servico no banco
    servico.pecas_ass.append(peca)
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