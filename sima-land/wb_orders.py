import requests
from time import time, sleep
import json
from datetime import datetime, timedelta
import pytz  

def check_14():
    moscow_tz = pytz.timezone('Europe/Moscow')  
    function_executed = int(open('flag_for_check_orders.txt').read())
    now_time = datetime.now(moscow_tz)  
    fourteen_time = now_time.replace(hour=13, minute=20, second=0, microsecond=0)  
    if (now_time > fourteen_time):  
        if not function_executed:
            with open('flag_for_check_orders.txt', 'w') as file:
                print('1', file=file)   
            return 1
    else:  # Если время до следующей 14:00  
        if function_executed: # Если функция уже была выполнена, сбрасываем флаг на следующий день  
            with open('flag_for_check_orders.txt', 'w') as file:
                print('0', file=file)
    return 0

def seconds_since_last_1400_msk():  
    msk_tz = pytz.timezone('Europe/Moscow')  
    now_msk = datetime.now(msk_tz)  
    last_1400 = now_msk.replace(hour=13, minute=20, second=0, microsecond=0)  
    if now_msk < last_1400:  
        last_1400 -= timedelta(days=1)  
    seconds_passed = (now_msk - last_1400).total_seconds()  
    return seconds_passed 

def convert_datetime_to_msk_format(iso_datetime):  
    utc_dt = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))  
    msk_tz = pytz.timezone('Europe/Moscow')  
    msk_dt = utc_dt.astimezone(msk_tz)  
    formatted_date = msk_dt.strftime("%d.%m.%y|%H:%M:%S")  
    return formatted_date 

def get_qty(ids):
    url = f'https://www.sima-land.ru/api/v3/item/?sid={",".join(list(ids.keys()))}&expand=stocks&fields=min_qty,sid'
    r = requests.get(url).json()
    m_q = {}
    for i in r['items']:
        m_q[i['sid']] = i['min_qty'] * ids[str(i['sid'])]
    return m_q

def check_decline_orders(ids):
    api = open('api_wb_orders.txt').read().strip()
    headers = {'Authorization': api, "Content-type": 'application/json'}
    json_data = {"orders": ids}
    r = 'https://marketplace-api.wildberries.ru/api/v3/orders/status'
    r = requests.post(r, headers=headers, json=json_data).json()
    try:
        decl_orders = list(filter(lambda x: x if x else '', [i['id'] if i['wbStatus'] == 'declined_by_client' else '' for i in r['orders']]))
    except:
        decl_orders = []
    return decl_orders

def get_orders(): # Получение новых заявок с момента последней проверки новых заявок
    t = int(time()) - int(seconds_since_last_1400_msk())
    api = open('api_wb_orders.txt').read().strip()
    headers = {'Authorization': api, "Content-type": 'application/json'}
    r = requests.get(f'https://marketplace-api.wildberries.ru/api/v3/orders?limit=1000&next=0&dateFrom={t}', headers=headers).json()
    orders = {i['id']: i for i in r['orders']}
    decline_orders = check_decline_orders(list(orders.keys()))
    for i in decline_orders:
        del orders[i]
    ids = {}
    try:
        for i in list(orders.values()):
            ids[str(i['warehouseId'])] = ids.get(str(i['warehouseId']), [])
            if i['article'].isdigit():
                ids[str(i['warehouseId'])].append(i['article'])
        for i in ids:
            ids[i] = {ids[i][j]: ids[i].count(ids[i][j]) for j in range(len(ids[i]))}
    except:
        pass
    return ids

def json_w(ids):
    try:
        with open('orders.json', encoding='utf-8') as file:
            data = json.load(file)
        if list(ids.values()) == list(data.values()):
            # print('ids = data')
            return {}
        with open('orders.json', 'w', encoding='utf-8') as file:
            json.dump(ids, file)
    except:
        with open('orders.json', 'w', encoding='utf-8') as file:
            json.dump(ids, file, ensure_ascii=False, indent=4)
    return ids

def close_order(order_id):
    sima_key = open('API_sima-land.txt').read().strip()
    headers = {'x-api-key': sima_key}
    json_data = {"jp_order_status_id": 2}
    try:
        r = requests.put(f'https://www.sima-land.ru/api/v3/jp-order/{order_id}/', headers=headers, json=json_data).json()
        print(f'статус заявки {r["order_id"]}: {r["jp_order_status_id"]}.')
    except:
        print(r['order_id'], 'Не удалилась(')
        sleep(15)


def make_order(items_ids):
    sima_key = open('API_sima-land.txt').read().strip()
    headers = {'x-api-key': sima_key}
    r = requests.get('https://www.sima-land.ru/api/v3/user', headers=headers).json() 
    user_id, user_email, user_phone = r['items'][0]['id'], r['items'][0]['email'], r['items'][0]['phone']
    def make_purchase(flag=1):
        if flag:
            try:
                with open('purshade_id.txt') as file:
                    purshade_id = int(file.read())
                    return purshade_id
            except:
                pass
        current_date = datetime.now()  
        next_day_date = current_date + timedelta(days=3)  
        formatted_date = next_day_date.strftime("%Y-%m-%d")
        json_data = {"ended_at": formatted_date, "user_id": user_id, "jp_status_id": 1}
        r = requests.post('https://www.sima-land.ru/api/v3/jp-purchase/', headers=headers, json=json_data).json()
        purshade_id = r['id']
        with open('purshade_id.txt', 'w') as file:
            print(str(purshade_id), file=file)
        return purshade_id
    def make_application(purshade_id):
        items_data = [{"item_sid": int(i), "qty": items_ids[i]} for i in items_ids]
        json_data = {"items_data": items_data, "contact_phone": user_phone, "contact_name": "Собственный заказ", "contact_email": user_email, "jp_purchase_id": purshade_id}
        r = requests.post('https://www.sima-land.ru/api/v3/order/checkout-jp-request-by-products/', headers=headers, json=json_data).json()
        if r == [{'field': 'jp_purchase_id', 'message': 'Невозможно участвовать в данной покупке'}]:
            return make_application(make_purchase(0))
        order_id = r['jp_order']['order_id']
        return order_id
    order_id = make_application(make_purchase())
    print(f'Заявка была создана. Id заявки: {order_id}')
    return order_id

def sima_ord(data):
    with open('orders_ids.json', encoding='utf-8') as file:
        orders_ids = json.load(file)
    for warehouseId in orders_ids:
        if orders_ids[warehouseId]:
            with open('del_orders_ids.txt', 'a') as file:
                print(str(orders_ids[warehouseId]), file=file)
            close_order(orders_ids[warehouseId])
            orders_ids[warehouseId] = 0
            sleep(5)
    for i in data:
        ids = data[i]
        qty_ids = get_qty(ids)
        ord_id = make_order(qty_ids)
        orders_ids[i] = ord_id
    with open('orders_ids.json', 'w', encoding='utf-8') as file:
            json.dump(orders_ids, file, ensure_ascii=False, indent=4)

def main_orders():
    if check_14():
        with open('orders.json', 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
        with open('orders_ids.json', 'w', encoding='utf-8') as file:
            json.dump({"899994": 0, "1136826":  0}, file, ensure_ascii=False, indent=4)
    with open('del_orders_ids.txt') as file:
        f = file.read().split()
        if len(f) > 1:
            ids = [int(i.strip()) for i in f][-5:0]
            for id in ids:
                close_order(id)
            with open('del_orders_ids.txt', 'w') as file:
                ids = '\n'.join(ids)
                print(ids, file=file)
    wb_orders = get_orders()
    json_orders = json_w(wb_orders)
    if not json_orders: return
    sima_ord(json_orders)
    
 
if __name__ == '__main__':
    a = get_orders()
    print(a)
    
