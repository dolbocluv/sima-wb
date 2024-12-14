import gspread
from time import sleep


gc = gspread.service_account(filename='service_account.json')
sheet = gc.open('УправлениеСимаЛенд')
ws = sheet.worksheet('FLAG')

def get_flag_file():
    with open('flag.txt') as flag_file:
        return int(flag_file.read())
    
def get_flag_gsh():
    flag = int(ws.acell('A1').value)
    return flag

def ch_flag_file_1():
    if get_flag_gsh():
        with open('flag.txt', 'w') as flag_file:
            print('1', file=flag_file)
        
def ch_flag_file_0():
    with open('flag.txt', 'w') as flag_file:
        print('0', file=flag_file)
        
def ch_flag_gsh_1():
    ws.update('A1', '1')
    
def ch_flag_gsh_0():
    ws.update('A1', '0')

if __name__ == '__main__':
    while True:
        sleep(7.5)
        if not get_flag_gsh():
            ch_flag_file_0()
    

    