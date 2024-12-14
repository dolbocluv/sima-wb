import requests
from time import sleep
from sima_p import parsing
from check_0_avb import check_0_avbs
from calc import calculation
from sh_work import sheet_change
import json

api = open('api_wb.txt').read().strip()
warehouse_id = 899994
headers = {'Authorization': api, "Content-type": 'application/json'}


def data_filter_for_wb(data):
    data_new = []
    for i in data:
        try:
            data_new.append([i[2], i[4], i[5], i[6], i[19]])
        except:
            data_new.append([i[2], i[4], i[5], i[6], 0])
    data = list(filter(lambda x: x if (x[0] and x[1]) else '', data_new))
    return data # [артикул вб, баркод, цена, скидка, наличие]

def up_prices(data):
    so_f_data = data_filter_for_wb(data)
    f_data = [{"nmID": int(i[0]), "price": int(i[2]), "discount": int(i[3])} for i in so_f_data]
    for i in range(1000):
        data_part = {"data": f_data[i*1000:(i+1)*1000]}
        r = requests.post('https://discounts-prices-api.wb.ru/api/v2/upload/task', json=data_part, headers=headers)
        if i*1000 >= len(f_data):
            return
        sleep(3)
        
def up_avb(data):
    so_f_data = data_filter_for_wb(data)
    f_data = [{"sku": str(i[1]), "amount": int(i[4])} for i in so_f_data]
    for i in range(1000):
        data_part = {"stocks": f_data[i*1000:(i+1)*1000]}
        r = requests.put(f"https://suppliers-api.wildberries.ru/api/v3/stocks/{warehouse_id}", json=data_part, headers=headers)
        if i*1000 >= len(f_data):
            return      
        sleep(3)


if __name__ == "__main__":
    parsed_data = parsing(100000)
    checked_data = check_0_avbs(parsed_data)
    calc_data = calculation(checked_data)
    new_data = sheet_change(calc_data)
    up_prices(new_data)
    up_avb(new_data)
    print('Программа закончила свою работу... ')