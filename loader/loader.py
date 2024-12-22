import requests
import json
import random

def read_json(file_path):     
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def set_register_data(role, i):
    name = role + str(i)
    return {
        'name': name,
        'email': f'{name}@gmail.com',
        'password': name,
        'phoneNumber': '0912345678',
        'role': role.upper()
    }

def set_login_data(role, i):
    name = role + str(i)
    return {
        'email': f'{name}@gmail.com',
        'password': name
    }

def set_store_data(store):
    data = read_json('./store_info.json')
    data['name'] = store['name']
    data['picture'] = store['picture']
    data['address'] = store['address']
    data['description'] = store['description']
    return data

def register(register_json):
    try:
        response = requests.post(
            url='http://localhost:8080/api/v2/auth/register',
            json=register_json,
            headers={
                'Content-Type': 'application/json'
            }
        )
        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(f'register error: {e}')

def login(login_json):
    try:
        response = requests.post(
            url='http://localhost:8080/api/v2/auth/login',
            json=login_json,
            headers={
                'Content-Type': 'application/json'
            }
        )
        print(response.status_code)
        print(response.json())
        token = response.json()['data']['token']
        storeId = response.json()['data']['storeId']
        return [token, storeId]
    except Exception as e:
        print(f'login error: {e}')
        
def get_store_info(storeId):
    try:
        response = requests.get(
            url=f'http://localhost:8080/api/v2/stores/{storeId}',
            headers={
                'Content-Type': 'application/json',
            }
        )
        print(response.status_code)
        print(response.json())
        menuId = response.json()['data']['menuId']
        return menuId
    except Exception as e:
        print(f'get store info error: {e}')
        
def update_store_info(token, storeId, store_info):
    try:
        response = requests.put(
            url=f'http://localhost:8080/api/v2/stores/{storeId}',
            json=store_info,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(f'update store info error: {e}')
        
def create_new_dish(token, menuId):
    try:
        response = requests.get(
            url=f'http://localhost:8080/api/v2/menu/{menuId}/dish/create',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        print(response.status_code)
        print(response.json())
        return response.json()['data']
    except Exception as e:
        print(f'create new dish error: {e}')
        
def update_dish(token, menuId, dishId, dish_json):
    try:
        response = requests.put(
            url=f'http://localhost:8080/api/v2/menu/{menuId}/dish/{dishId}',
            json=dish_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(f'update dish error: {e}')
        
def create_review():
    comments = [
        "已購買，小孩很愛吃",
        "已購買，小孩不愛吃",
        "已購買，小孩不喜歡",
        "已購買，小孩很喜歡",
        "已回購，小孩很喜歡",
        "已購買，下次不會買",
        "怎麼可以這麼好吃!",
        "怎麼可以這麼難吃!",
        "比我媽煮的還好吃",
        "比我媽煮的還難吃",
        "狗都不吃",
        "不吃粗的好粗",
        "已Mygo 小孩還在go"
    ]
    return {
        "averageSpend": float(random.randint(30, 100)),
        "comment": comments[random.randint(0, 12)],
        "rating": float(random.randint(1, 5))
    }
        
def add_review_to_store(token, storeId, review_json):
    try:
        response = requests.post(
            url=f'http://localhost:8080/api/v1/reviews/{storeId}',
            json=review_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(f'add review to store error: {e}')

stores = read_json('../crawler/stores_data.json')   
storeIds = []

store_types = ['breakfast', 'drink', 'fastfood']
for i in range(0, 50):
    # merchant register and login
    register(set_register_data('merchant', i))
    [token, storeId] = login(set_login_data('merchant', i))
    storeIds.append(storeId)
    
    # update store infomation
    update_store_info(token, storeId, set_store_data(stores[i]))
    menuId = get_store_info(storeId)
    store_type = store_types[i%3]
    
    # update menu dishes
    for j in range(1, 5):
        dishes = read_json(f'./{store_type}_category{j}.json')
        for dish in dishes:
            dishId = create_new_dish(token, menuId)
            update_dish(token, menuId, dishId, dish)


for i in range(0, 30):
    # customer register and login
    register(set_register_data('customer', i))
    [token, storeId] = login(set_login_data('customer', i))
    
    # add review to store
    number = random.randint(10, 30)
    start = random.randint(0, 49)
    for j in range(number):
        now = (start + j) % 50
        add_review_to_store(token, storeIds[now], create_review())
        