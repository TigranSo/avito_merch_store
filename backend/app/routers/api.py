import os
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.app import models, schemas, database
from backend.app.services import auth as auth_service
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api")

SECRET_KEY = os.getenv("SECRET_KEY", "esfesf568s6f58esfsf5sfse3fse9f")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Генерация JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(database.get_db)):
    """Получить текущего авторизованного пользователя"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/auth", response_model=schemas.AuthResponse)
def auth(auth_req: schemas.AuthRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == auth_req.username).first()
    if not user:
        # Автоматически создание пользователя при первой аутентификации
        hashed_pw = auth_service.get_password_hash(auth_req.password)
        user = models.User(username=auth_req.username, hashed_password=hashed_pw, balance=1000)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not auth_service.verify_password(auth_req.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    return {"token": token}


@router.get("/info", response_model=schemas.InfoResponse)
def get_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    """информацию о своих монетах"""
    coins = current_user.balance
    # Получаю инвентарь купленные товары
    purchases = db.query(models.Purchase).filter(models.Purchase.user_id == current_user.id).all()
    inventory_dict = {}
    for purchase in purchases:
        merch_item = db.query(models.Merch).filter(models.Merch.id == purchase.merch_id).first()
        if merch_item:
            inventory_dict[merch_item.name] = inventory_dict.get(merch_item.name, 0) + 1
    inventory = [{"type": name, "quantity": qty} for name, qty in inventory_dict.items()]
    
    # История монет транзакции отправки и получения
    received_transactions = db.query(models.Transaction).filter(models.Transaction.receiver_id == current_user.id).all()
    sent_transactions = db.query(models.Transaction).filter(models.Transaction.sender_id == current_user.id).all()
    received = []
    for tx in received_transactions:
        sender = db.query(models.User).filter(models.User.id == tx.sender_id).first()
        if sender:
            received.append({"fromUser": sender.username, "amount": tx.amount})
    sent = []
    for tx in sent_transactions:
        receiver = db.query(models.User).filter(models.User.id == tx.receiver_id).first()
        if receiver:
            sent.append({"toUser": receiver.username, "amount": tx.amount})
    coin_history = {"received": received, "sent": sent}
    
    return {"coins": coins, "inventory": inventory, "coinHistory": coin_history}


@router.post("/sendCoin", status_code=200)
def send_coin(req: schemas.SendCoinRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    """переводы монет между сотрудниками"""
    recipient = db.query(models.User).filter(models.User.username == req.toUser).first()
    if not recipient:
        raise HTTPException(status_code=400, detail="Recipient user not found")
    if current_user.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    current_user.balance -= req.amount
    recipient.balance += req.amount
    tx = models.Transaction(sender_id=current_user.id, receiver_id=recipient.id, amount=req.amount)
    db.add(tx)
    db.commit()
    return {"message": "Coins sent successfully"}


@router.get("/buy/{item}", status_code=200)
def buy_item(item: str = Path(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    """покупка мерча за монеты"""
    merch_item = db.query(models.Merch).filter(models.Merch.name.ilike(item)).first()
    if not merch_item:
        raise HTTPException(status_code=400, detail="Merch item not found")
    if current_user.balance < merch_item.price:
        raise HTTPException(status_code=400, detail="Insufficient coins to buy this item")
    current_user.balance -= merch_item.price
    purchase = models.Purchase(user_id=current_user.id, merch_id=merch_item.id)
    db.add(purchase)
    db.commit()
    return {"message": f"Purchased {merch_item.name} successfully"}


@router.get("/merch", response_model=List[schemas.MerchResponse])
def list_merch(db: Session = Depends(database.get_db)):
    """получить список всех доступных товаров"""
    merch_items = db.query(models.Merch).all()
    return merch_items