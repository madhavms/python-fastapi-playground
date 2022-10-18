from math import prod
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from load_dotenv import load_dotenv


env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

print(f'password={REDIS_PASSWORD}')

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
    password=REDIS_PASSWORD, #password stored in env file
    decode_responses=True
)

class Product(HashModel):
    name:str
    price:float
    quantity:int

    class Meta:
        database = redis


@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        'id':product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post('/products')
def create(product:Product):
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
        res = "Sorry product not found"
    return res

@app.delete('/products/{pk}')
def get(pk: str):
    
    res = Product.delete(pk)
    return f'Product has been deleted' if res == 1 else 'Product not found'