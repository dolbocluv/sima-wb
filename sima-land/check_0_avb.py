from sima_p import parsing
from time import time
import json


def check_0_avbs(data): # data = list of [name, sid, wholesale_price, min_qty, avb[0], avb[1], avb[2]]
    def m_ret_data(data, new_data):
        data = {i[1]: i for i in data}
        return_data = [data[i][:4] + list(new_data[i].values())  for i in data]
        return return_data
    with open('chck_0_avb.json', 'r', encoding='utf-8') as file:  
        old_data = json.load(file)
    new_time = int(time())

    new_data = {i[1]: {'1': [i[4], 0, new_time], '2': [i[5], 0, new_time], '115': [i[6], 0, new_time]} for i in data}
                                   # этот 0 - количество дней, которое не менялось наличие
    for sid in new_data:
        old_data[sid] = old_data.get(sid, new_data[sid])
        for i in ['1', '2', '115']:
            if new_data[sid][i][0] == 0: # Если наличие != 0, то количество дней без изменений будет = 0
                new_data[sid][i][1] = int((new_time - old_data[sid][i][2]) / (60 * 60 * 24))
                new_data[sid][i][2] = old_data[sid][i][2]

    new_data['last_check'] = new_time

    with open('chck_0_avb.json', 'w', encoding='utf-8') as file:  
        json.dump(new_data, file, ensure_ascii=False, indent=4)

    return_data = m_ret_data(data, new_data)
    return return_data 


if __name__ == "__main__":
    parsed_data = parsing(1)
    print(check_0_avbs(parsed_data))
    print('Программа закончила свою работу... ')
