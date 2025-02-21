from fastapi import APIRouter, HTTPException
from database import get_engine
from models.models import Peca
from odmantic import ObjectId

router = APIRouter(
    prefix="/pecas", # Prefixo referente a rota
    tags=["Peças"], # Tag para a documentação
)

# Motor
engine = get_engine()

# Rota para pegar todos as Peca do banco
@router.get("/pecas/", response_model= list[Peca])
async def get_all_peca()-> list[Peca]:
    list_peca = await engine.find(Peca)
    return list_peca

# Rota para pegar uma peça por id
@router.get("/pecas/{peca_id}", response_model= Peca)
async def get_peca(peca_id: str)-> Peca:
    peca = await engine.find_one(Peca, Peca.id == ObjectId(peca_id))
    if not peca:
        raise HTTPException(status_code=404, detail="Peca não encontrada")
    return peca

# Rota para inserir um novo Peca no banco
@router.post("/pecas/", response_model= Peca)
async def create_peca(peca: Peca)-> Peca:
    # Verifica se já existe uma peça com o mesmo nome
    peca_exist = await engine.find_one(Peca, Peca.nome == peca.nome)
    if peca_exist:
        raise HTTPException(status_code=400, detail="Peça já cadastrada")
    # Insere a peça no banco
    await engine.save(peca)
    return peca


# Rota para alterar dados de uma peça
@router.put("/pecas/", response_model=Peca)
async def update_peca(peca_id: str, peca_data: dict)-> Peca:
    # verifica se o Peca esta no banco
    peca = await engine.find_one(Peca, Peca.id == ObjectId(peca_id))
    if not peca:
        raise HTTPException(status_code=404, detail="Peca não encontrada")
    # Substitui os campos que foram modificados
    for key, value in peca_data.items():
        setattr(peca, key, value)
    # Salva o Peca atualizado
    await engine.save(peca)
    return peca

# Rota para deletar uma peça
@router.delete("/pecas/{peca_id}")
async def delete_peca(peca_id: str)-> dict:
    peca= await engine.find_one(Peca, Peca.id == ObjectId(peca_id))
    if not peca:
        raise HTTPException(status_code=404, detail="Peca não encontrada")
    await engine.delete(peca)
    return {"msg": "Peca excluida com sucesso"}


