from sima_p import parsing, op_sh, up_sh
from check_0_avb import check_0_avbs
from calc import calculation
import time
    
    
def sheet_change(new_data): # new_data = # dict of {sid: [price, discount, disc-pr, spp pr, wholes_pr, min_qty, ff, pp, pay_for_time, logist, tax, profit, op_pr, avb[0], days, avb[1], days, avb[2], days]}
    #print(*list(new_data.values()), sep='\n')
    old_data = op_sh('price_calculation')
    t1 = int(time.time())
    data = {i[3]: i for i in old_data}
    for sid in data:
        new_item = new_data.get(sid, data[sid][5:19] + [0, 99, 0, 99, 0, 99])
        data[sid] = data[sid][:5] + new_item
    data = list(data.values())
    t2 = int(time.time())
    if abs(t2 - t1) < 15:
        time.sleep(15 - (t2 - t1))
    up_sh('price_calculation', data, f'A2:Y{len(data) + 1}')
    return data
    

if __name__ == "__main__":
    parsed_data = parsing(1)
    checked_data = check_0_avbs(parsed_data)
    calc_data = calculation(checked_data)
    sheet_change(calc_data)
    print('Программа закончила свою работу... ')
