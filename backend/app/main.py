from fastapi import FastAPI
from backend.app.routers import api
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import Merch

app = FastAPI(title="API Avito shop")

merch_items = [
    {"name": "t-shirt", "price": 80},
    {"name": "cup", "price": 20},
    {"name": "book", "price": 50},
    {"name": "pen", "price": 10},
    {"name": "powerbank", "price": 200},
    {"name": "hoody", "price": 300},
    {"name": "umbrella", "price": 200},
    {"name": "socks", "price": 10},
    {"name": "wallet", "price": 50},
    {"name": "pink-hoody", "price": 500},
]

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        merch_count = session.query(Merch).count()
        if merch_count == 0:
            for item in merch_items:
                new_merch = Merch(name=item["name"], price=item["price"])
                session.add(new_merch)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

app.include_router(api.router)
