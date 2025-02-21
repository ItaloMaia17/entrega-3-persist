from fastapi import APIRouter

router = APIRouter(
    prefix= "", # Prefixo para todas as rotas
    tags=["Home"], # Tag para documentação
)

#Home
@router.get("/")
async def root():
    return {"msg": "Bem-vindo a G&I_Tech!"}