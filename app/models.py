from pydantic import BaseModel


class HistoricalTransaction(BaseModel):
    id: int
    provider_id: int
    transaction_value: int


class IncomingTransactions(BaseModel):
    id: int
    value: int


class InitialData(BaseModel):
    id: int
    provider_name: str
    initial_value: int


class KeyDBModel(BaseModel):
    key: str
    value: int
