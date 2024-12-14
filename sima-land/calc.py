from sima_p import op_sh, parsing
from check_0_avb import check_0_avbs
import telebot

def send_exc(exc):
    bot = telebot.TeleBot('5438228689:AAHEkUTFlwABJiNHYw372VNxwzk7V0d19FE') 
    bot.send_message(1208368841, exc)


def calculation(data): # data = [name, sid, wholesale_price, min_qty, avb[0], days, avb[1], days, avb[2], days]
    calc_data = {}
    coefs_f = [i[:8] for i in op_sh('coefficients')]
    coefs = list(filter(lambda x: x if x[0] else '', coefs_f))
    print(coefs)
    for i in range(len(coefs)):
        coefs[i][0] = list(map(int, coefs[i][0].split('-')))
        for j in range(1, len(coefs[i])):
            coefs[i][j] = float(coefs[i][j].replace(',', '.'))  
    
    def get_coefs(price): 
        for i in coefs:
            if i[0][0] <= price <= i[0][1]:
                return i[1:] # [Кэф. на цену закупа, Скидка, Цена ФФ, Цена ПП, Коэфф. платы за время, Цена лог-ка, Коэфф. налога]
                      
    for item in data: # item = [name, sid, wholesale_price, min_qty, avb[0], avb[1], avb[2]]
        price = item[2]
        if price == 0:
            send_exc(f'Ошибка. У товара нет оптовой цены. sid: {item[1]}')
            price = 50000
        wholesalePrice = int(price * 0.92 * item[3])
        price*= item[3]
        item_coefs = get_coefs(price)
        avb = item[4:7] # [1, 0, 1727124057], [0, 0, 1727124057], [1, 0, 1727124057]
        avbs = [avb[0][0], avb[0][1], avb[1][0], avb[1][1], avb[2][0], avb[2][1]]
        calc_item = []
        calc_item.append(int(price * item_coefs[0])) # 0 price
        calc_item.append(int(item_coefs[1])) # 1 discount
        calc_item.append(int(calc_item[0] * (1 - calc_item[1] / 100))) # 2 discount-price
        calc_item.append(int(calc_item[2] * 0.8)) # 3 spp price
        calc_item.append(int(price)) # 4 wholesale_price
        calc_item.append(wholesalePrice) # 5 wholesalePrice without discount
        calc_item.append(int(item[3])) # 6 min_qty
        calc_item.append(int(item_coefs[2])) # 7 full f
        calc_item.append(int(item_coefs[3])) # 8 pp
        calc_item.append(round(calc_item[2] * float(item_coefs[4]), 1)) # 9 pay for time
        calc_item.append(int(item_coefs[5])) # 10 logistics
        calc_item.append(round(calc_item[2] * item_coefs[6], 2)) # 11 tax
        calc_item.append(round(calc_item[3] - (sum(calc_item[5:]) - item[3]), 2)) # 12 profit
        calc_item.append(round(calc_item[-1] / calc_item[3], 2)) # 13 op pr
        calc_item.extend(avbs) # 14,15,16,17 avaibility
        calc_data[str(item[1])] = calc_item
    return calc_data # dict of {sid: [price, discount, discount-price, spp price, wholes_price, wholes_price with discount, min_qty, full f, pp, pay_for_time, logistics, tax, profit, op_pr, avb[0], days, avb[1], days, avb[2], days]}
    
     
if __name__ == "__main__":
    parsed_data = parsing(1)
    checked_data = check_0_avbs(parsed_data)
    calc_data = calculation(checked_data)
    for i in calc_data:
        print(i, ':', calc_data[i])
    print()
    print('Программа закончила свою работу... ')