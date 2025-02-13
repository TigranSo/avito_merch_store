from pydantic import BaseModel
from typing import List


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str


class SendCoinRequest(BaseModel):
    toUser: str
    amount: int


class InventoryItem(BaseModel):
    type: str
    quantity: int


class CoinHistoryItemReceived(BaseModel):
    fromUser: str
    amount: int


class CoinHistoryItemSent(BaseModel):
    toUser: str
    amount: int


class CoinHistory(BaseModel):
    received: List[CoinHistoryItemReceived] = []
    sent: List[CoinHistoryItemSent] = []


class InfoResponse(BaseModel):
    coins: int
    inventory: List[InventoryItem] = []
    coinHistory: CoinHistory


class ErrorResponse(BaseModel):
    errors: str


class MerchResponse(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        orm_mode = True