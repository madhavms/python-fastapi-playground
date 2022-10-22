from math import prod
import time

import requests
from main import redis, Product
import sys
sys.path.insert(0,'/Users/madhavmanohar/Desktop/fast-api-playground/python-fastapi-playground/src/')
from payment.main import Order


key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)

except:
    print('Group already exists!')

while True:
    try:
        results = redis.xreadgroup(group, key, {key:'>'}, None)
        print("RESULT",results)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                print("OBJ----",obj)
                product = Product.get(obj['product_id'])
                qty = product.quantity - int(obj['quantity'])
                print("QTY: ",qty)
                if qty < 0:
                    status = 'refunded'
                else:
                    status = 'completed'
                    product.quantity = qty
                    product.save()

                requests.patch(f'http://localhost:8003/orders', json={"pk":obj['pk'], "status": status})

    except Exception as e:
        print(str(e))
    time.sleep(1)