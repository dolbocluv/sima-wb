import requests
import gspread


def op_sh(name):
    for _ in range(10):
        try:
            gc = gspread.service_account(filename='service_account.json')
            sheet = gc.open('УправлениеСимаЛенд')
            items_sh = sheet.worksheet(name)
            items_l = items_sh.get_all_values()[1:]
            return items_l
        except: print('Таблица не открылась. ')
    else: return []  
def up_sh(name, data, interval):
    for _ in range(10):
        try:
            gc = gspread.service_account(filename='service_account.json')
            sheet = gc.open('УправлениеСимаЛенд')
            sheet = sheet.worksheet(name)
            break
        except: print('Таблица не обновилась. ')
    sheet.update(data, interval)
    
def parsing(predel=100000):
    coefs_f = [i[10:] for i in op_sh('coefficients')]
    coefs = list(filter(lambda x: x if x else '', coefs_f))
    sh_data = op_sh('price_calculation')
    s_ids = [i[3] for i in sh_data]
    p_data = []
    
    sima_api = open('API_sima-land.txt').read().strip()
    headers = {'x-api-key': sima_api}
    for i in range(predel):
        if i * 50 >= len(s_ids):
            break
        url = f'https://www.sima-land.ru/api/v3/item/?sid={",".join(s_ids[i*50:(i+1)*50])}&expand=stocks&fields=name,sid,stocks,wholesale_price,price,min_qty'
        for _ in range(3):
            try:
                r = requests.get(url, headers=headers).json()
                break
            except:
                pass
        for item in r['items']:
            price = min(int(item['wholesale_price']), int(item['price']))
            avb = change_avb(item['stocks'], price, coefs)
            p_data.append([item['name'], str(item['sid']), price, item['min_qty'], avb[0], avb[1], avb[2]])
    return p_data # data = list of [name, sid, wholesale_price, min_qty, avb]

def change_avb(stocks, price, coefs):
    pr_diaps = []
    for i in coefs:
        if i[0] and i[1]:
            pr_diaps.append(i)
        else:
            break
    def get_avb_quantity(pr):
        if pr <= 50:
            return 150
        elif pr <= 90:
            return 100
        elif pr <= 250:
            return 40
        elif pr <= 1000:
            return 20
        else:
            return 10
    avbs = {1: 0, 2: 0, 115: 0}
    for stock in stocks:
        if stock['stock_id'] in [2, 115]:
            if stock.get('balance_text', '') == 'Достаточно':
                balance = get_avb_quantity(price)
            else:
                balance = stock.get('balance', 0)
            for i in pr_diaps:
                if i[0]:
                    pr_diap = list(map(int, i[0].split('-')))
                    if pr_diap[0] <= balance <= pr_diap[1]:
                        avbs[stock['stock_id']] = int(i[1])
    main_kolvos = list(avbs.values())
    return main_kolvos


if __name__ == "__main__":
    data = parsing(1)
    print(*data, sep='\n', end='\n\n')
    print('Программа закончила свою работу... ')