from functools import total_ordering
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from load_dotenv import load_dotenv
from starlette.requests import Request
import requests,time
from fastapi.background import BackgroundTasks


env_path = Path('..')/'.env'
load_dotenv(dotenv_path=env_path)

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host='redis-11314.c14.us-east-1-2.ec2.cloud.redislabs.com',
    port=11314,
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

    class Meta:
        database = redis

@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    #one microservice calls another using requests
    res = requests.get(f'http://localhost:8001/products/{body["id"]}')
    print(res)
    product = res.json()
    print(product)
    order = Order(
        product_id= body['id'],
        price= product['price'],
        fee= 0.2*product['price'],
        total= 1.2*product['price'],
        quantity= product['quantity'],
        status= 'pending'
    )
    order.save()
    #from fastapi.background
    background_tasks.add_task(order_completed, order)
    return format(order)

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    print(order)
    order.save()

def format(order : Order):
    return {
        'order_id': order.pk,
        'product_id': order.product_id,
        'price': order.price,
        'fee': order.quantity,
        'total': order.quantity,
        'quantity': order.quantity,
        'status': 'pending'
    }
