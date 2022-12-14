from functools import total_ordering
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.encoders import jsonable_encoder
import os
from dotenv import load_dotenv, find_dotenv
from starlette.requests import Request                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
import requests
import time
from fastapi.background import BackgroundTasks
from utils import global_var
import datetime


env_path = Path('..')/'.env'
load_dotenv(find_dotenv())


REDIS_HOST = os.getenv('REDIS_HOST')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_PORT = os.getenv('REDIS_PORT')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,  # password stored in env file
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded
    created_timestamp: str
    last_update_timestamp: str

    class Meta:
        database = redis


#Returns all the orders
@app.get('/orders')
def get():
    pks = Order.all_pks()
    res = [Order.get(pk) for pk in pks]

    return res if res else "No orders to display"




@app.get('/orders/{pk}')
def get(pk: str):
    try:
        res = Order.get(pk)
    except:
        res = global_var.PRODUCT_NOT_FOUND
    return res

@app.patch('/orders')
async def update(request: Request):
    body = await request.json()
    print(body)
    order = Order.get(body["pk"])
    order.status = body["status"]
    order.save()
    return order

@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    # one microservice communicates with another using requests http library
    try:
        res = requests.get(f'http://localhost:8001/products/{body["id"]}')
    except:
        return "Unable to create order at the moment. Please contact support."

    product = res.json()
    if product == global_var.PRODUCT_NOT_FOUND:
        return product

    if product['quantity'] == 0 or product['quantity'] < body['quantity']:
        return f"Requested qty not available for {product['name']}. In stock qty: {product['quantity']}"

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        quantity=body['quantity'],
        status='pending',
        created_timestamp=str(datetime.datetime.now()),
        last_update_timestamp=str(datetime.datetime.now())
    )
    order.save()
    # from fastapi.background
    background_tasks.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(5)
    order.save()
    redis.xadd('order_completed', order.dict(), '*')



@app.delete('/orders')
def get():
    pks = Order.all_pks()
    res_arr = []
    for pk in pks:
        res = Order.delete(pk)
        res = f'Order {pk} has been deleted' if res == 1 else 'Order {pk} not deleted'
        res_arr.append(res)
    
    return res_arr if res_arr else "No orders to delete!"


