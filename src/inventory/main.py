from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from utils import global_var

from dotenv import load_dotenv, find_dotenv


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


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post('/products')
def create(product: Product):
    try:
        saved = product.save().pk
    except:
        saved = "An error occured while saving"
    return 1


@app.get('/products/{pk}')
def get(pk: str):
    try:
        res = Product.get(pk)
    except:
        res = global_var.PRODUCT_NOT_FOUND
    return res


@app.delete('/products/{pk}')
def get(pk: str):

    res = Product.delete(pk)
    return f'Product has been deleted' if res == 1 else 'Product not found'
