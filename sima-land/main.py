from time import sleep, strftime
from sima_p import parsing
from check_0_avb import check_0_avbs
from calc import calculation, send_exc
from sh_work import sheet_change
from wb_api import up_prices, up_avb
from wb_orders import main_orders
from flag_checker import get_flag_file, ch_flag_file_1

def main():    
    while True:
        try:
            main_orders()
            parsed_data = parsing(100000)
            checked_data = check_0_avbs(parsed_data)
            calc_data = calculation(checked_data)
            if get_flag_file():
                new_data = sheet_change(calc_data)
                up_prices(new_data)
                up_avb(new_data)
                print(f'{strftime("%d.%m %H:%M:%S")} - Данные обновлены... \n')
    
            else:
                sleep(120)
                ch_flag_file_1()
        except Exception as exc:
            send_exc(exc)
            print(f'{strftime("%d.%m %H:%M:%S")} - {exc}... \n', end='\n\n')

if __name__ == '__main__':
    main()