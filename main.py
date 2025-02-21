from fastapi import FastAPI
from routes import home, dispositivo, peca, servico, tecnico

app = FastAPI()

app.include_router(home.router)
app.include_router(dispositivo.router)
app.include_router(peca.router)
app.include_router(servico.router)
app.include_router(tecnico.router)    

