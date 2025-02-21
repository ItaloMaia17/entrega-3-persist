import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

#Carrega as variaveis de ambiente
load_dotenv()

# Conexão com o banco
url = os.getenv("DATABASE_URL")
client = AsyncIOMotorClient(url)
# Seleciona o database, cria um novo caso não exista
db = client.assistencia
engine = AIOEngine(client = client, database= "assistencia")

# Pega a conexão
def get_engine() -> AIOEngine:
    return engine
    

