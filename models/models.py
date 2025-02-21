from odmantic import Model, Reference, ObjectId
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, List


class Dispositivo(Model):
    modelo: str
    tipo: str
    fabricante: str

class Peca(Model):
    nome: str
    fabricante: str
    preco: float

class Tecnico(Model):
    nome: str
    especialidade: str
    contato: str
    salario: float

class Servico(Model):
    tipo_de_servico: str
    descricao: str
    valor: float
    cadastrado_em: datetime = datetime.now(timezone.utc)
    dispositivo: Dispositivo= Reference()
    tecnico: Tecnico= Reference()   
    pecas_ids: List[Peca]= [] #ids das peças utilizadas no serviço