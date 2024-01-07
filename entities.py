import uuid
from typing import Dict

from pydantic import BaseModel


class RequestUnbagQuery(BaseModel):
    """
    Запрос на распаковку bag файла
    """
    id: uuid.UUID
    operation_type: str
    files: list[str]
    output_path: str
    params: dict

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            uuid.UUID: lambda x: str(x)
        }


class RequestQuery(BaseModel):
    """
    Запрос на выполнение операции над облаком точек
    """
    id: uuid.UUID
    operation_type: str
    file: str
    output_path: str
    params: Dict[str, str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            uuid.UUID: lambda x: str(x)
        }


class ResponseQuery(BaseModel):
    """
    Ответ на запрос
    """
    id: uuid.UUID
    operation_type: str
    file: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            uuid.UUID: lambda x: str(x)
        }
