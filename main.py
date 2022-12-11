from api import get_all_urls, get_zakupka, get_contract, is_bad_token, set_token, ZAKUPKI_URL_NAME, CONTRACT_URL_NAME
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.messagebox import showinfo
import threading
import time
import math
import datetime
import pandas as pd
import os


SAVE_DIR_NAME = "Закупки и контракты"


def save_data(items, dir_name):
    user_path = os.path.expanduser('~')
    save_dir = os.path.join(user_path, "Documents", SAVE_DIR_NAME)

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    df = pd.DataFrame(items)
    df.to_excel(os.path.join(save_dir, dir_name))


def on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")


def bad_token(mes):
    showinfo(title='Error', message=mes)


def downloaded():
    showinfo(title='Information', message='Загружено!')


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.bind_all("<Key>", on_key_release, "+")
        self.title('Закупки и контракты')
        self.token = tk.StringVar()
        self.wind_with = 500
        self.wind_height = 200
        self.x = int(self.winfo_screenwidth() / 2 - self.wind_with / 2)
        self.y = int(self.winfo_screenheight() / 2 - self.wind_height / 2)
        self.geometry(f'{self.wind_with}x{self.wind_height}+{int(self.x)}+{int(self.y)}')

        # token entry
        self.token_entry = ttk.Entry(textvariable=self.token, width=42)
        self.token_entry.insert(0, "https://dev.gosplan.info/dashboard")
        self.token_entry.pack(pady="10")

        # download button
        self.download_button = tk.Button(self, text='Загрузить закупки и контракты',
                                         width=27, command=self.create_thread)
        self.download_button.pack(pady="2")

        self.myFont = font.Font(size=20)
        self.download_button['font'] = self.myFont

        # progress bar
        self.pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280,
        )

        # label progress bar
        self.value_label = tk.Label(self)
        self.value_label['font'] = self.myFont

        # label urls are loaded
        self.download_label = tk.Label(self, text='Загрузка...')
        self.download_label['font'] = self.myFont

        # label time
        self.time_remain_label = tk.Label(self)
        self.time_remain_label['font'] = self.myFont

    def get_data(self, obj):
        items = obj['items']
        urls = obj['urls']
        print(len(urls))
        time_list = obj['time_list']
        name = obj['name']
        total = obj['total']
        counter = obj['counter']
        reverse_counter = obj['reverse_counter']

        for url in urls:
            start_time = time.time()

            if name == ZAKUPKI_URL_NAME:
                item = get_zakupka(url)
            else:
                item = get_contract(url)

            if item:
                items['Номер'].append(item['Номер'])

            counter += 1
            reverse_counter -= 1
            self.pb['value'] = round(100 * (counter / total), 1)
            self.value_label['text'] = self.set_progress()
            end_time = time.time() - start_time
            time_list.append(end_time)
            avg_time = math.ceil(sum(time_list) / len(time_list))
            self.time_remain_label['text'] = datetime.timedelta(seconds=avg_time * reverse_counter)

        return counter, reverse_counter

    def create_thread(self):
        thread = threading.Thread(target=self.start)
        thread.daemon = True
        thread.start()

    def set_progress(self):
        return f"Текущий прогресс: {self.pb['value']}%"

    def start(self):
        self.token_entry.pack_forget()
        self.download_button.pack_forget()
        self.download_label.pack()
        set_token(self.token.get())
        mes = is_bad_token()

        if mes:
            self.download_label.pack_forget()
            self.token_entry.pack(pady="10")
            self.download_button.pack(pady="2")
            bad_token(mes)
            return

        urls = get_all_urls()
        self.download_label.pack_forget()

        self.pb.pack(pady=20)
        self.value_label.pack(pady=5)
        self.time_remain_label.pack(pady=5)

        # zakupki_urls = urls[ZAKUPKI_URL_NAME]
        contract_urls = urls[CONTRACT_URL_NAME]
        total = len(contract_urls)

        print(f'Контрактов - {len(contract_urls)}')

        time_list = []
        counter = 0
        reverse_counter = total
        # zakupki = {
        #     'Номер': [],
        # }
        contracts = {
            'Номер': [],
        }
        params = {
            'items': None,
            'urls': None,
            'time_list': time_list,
            'name': None,
            'total': total,
            'counter': counter,
            'reverse_counter': reverse_counter
        }

        print('!!!!!!!!!!!!!!!!!!!!!ЗАКУПКИ')

        # params['items'] = zakupki
        # params['urls'] = zakupki_urls
        # params['name'] = ZAKUPKI_URL_NAME
        # counter, reverse_counter = self.get_data(params)

        print('!!!!!!!!!!!!!!!!!!!!!КОНТРАКТЫ')

        params['items'] = contracts
        params['urls'] = contract_urls
        params['name'] = CONTRACT_URL_NAME
        # params['counter'] = counter
        # params['reverse_counter'] = reverse_counter
        self.get_data(params)

        # save_data(zakupki, 'Закупки.xlsx')
        try:
            save_data(contracts, 'Контракты.xlsx')
        except Exception as e:
            user_path = os.path.expanduser('~')
            save_dir = os.path.join(user_path, "Documents", SAVE_DIR_NAME)
            f = open(os.path.join(save_dir, "log.txt"), "w")
            f.write(str(e))
            f.close()

        downloaded()
        self.time_remain_label.pack_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
