from functools import total_ordering
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
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


@app.get('/orders')
def get():
    return [format_order(pk) for pk in Order.all_pks()]


def format_order(pk):

    order = Order.get(pk)
    return {
        'order_id': order.pk,
        'product_id': order.product_id,
        'price': order.price,
        'fee': order.quantity,
        'total': order.quantity,
        'quantity': order.quantity,
        'status': 'pending',
        'created_timestamp': order.created_timestamp,
        'last_update_timestamp': order.last_update_timestamp
    }


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


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

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        quantity=product['quantity'],
        status='pending',
        created_timestamp=str(datetime.datetime.now()),
        last_update_timestamp=str(datetime.datetime.now())
    )
    order.save()
    # from fastapi.background
    background_tasks.add_task(order_completed, order)
    return format(order)


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    print(order)
    order.save()

@app.delete('/orders')
def get():
    pks = Order.all_pks()
    res_arr = []
    print("PKS", pks)
    if is_empty(pks):
        return "No orders to delete!"
    for pk in pks:
        res = Order.delete(pk)
        res = f'Order {pk} has been deleted' if res == 1 else 'Order {pk} not deleted'
        res_arr.append(res)
    return res_arr

def is_empty(generator):
    for item in generator:
        return False
    return True

def format(order: Order):
    return {
        'order_id': order.pk,
        'product_id': order.product_id,
        'price': order.price,
        'fee': order.quantity,
        'total': order.quantity,
        'quantity': order.quantity,
        'status': 'pending',
        'created_timestamp': order.created_timestamp,
        'last_update_timestamp': order.last_update_timestamp
    }
