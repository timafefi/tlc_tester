import aiohttp
import asyncio
import random
from websocket import create_connection
import logging
from datetime import datetime
import requests
from time import time
import config


class BaseAPI:
    def __init__(self, ip, buttcount, min_inte, max_inte, heap_inte):
        self.ip = f'http://{ip}'
        self.sockaddr = f"ws://{ip}:11181"
        self.ws = create_connection(self.sockaddr)
        self.buttcount = buttcount
        self.session = requests.Session()
        self.min_inte = min_inte
        self.max_inte = max_inte
        self.heap_inte = heap_inte
        self.start_time = time()

    async def connect_loop(self, cls):
        print(f"{cls} entered connect_loop")
        self.ws.close()
        done = False
        while (not done):
            try:
                self.ws = create_connection(self.sockaddr)
                done = True
            except Exception as e:
                logging.info(f"{cls}: ERROR: {e}. Trying again in 3s")
                await asyncio.sleep(3)
        print(f"{cls} exited connect_loop")





class Website(BaseAPI):
    def socket_requests(self, page):
        if (page == '' or page == 'settings'):
            self.ws.send("/getsettings")
            self.ws.recv()
            self.ws.send("/getssid")
            self.ws.recv()
        else:
            self.ws.send("/getnetscan")
            self.ws.recv()
            self.ws.send("/getcredentials")
            self.ws.recv()

    async def action(self):
        pages = ['', 'settings', 'wifi']
        while True:
            path = random.choice(pages)
            t = time()
            try:
                response = self.session.get(f'{self.ip}/{path}', timeout=10)
            except Exception as e:
                logging.info(f"LOAD_PAGE:    /{path} - {e}")
                await asyncio.sleep(20)
                continue
            try:
                self.socket_requests(path)
            except Exception:
                await self.connect_loop("LOAD_PAGE")
            r = random.randint(self.min_inte, self.max_inte)
            if response.status_code != 200:
                logging.info(f"LOAD_PAGE:    /{path} - ERR. Status code: "
                             f"{response.status_code}. Next run in {r}s")
            else:
                logging.info(f"LOAD_PAGE:    /{path} - OK ({time() - t})."
                             f" Next run in {r}s")
            await asyncio.sleep(r)


class Pult(BaseAPI):
    async def action(self):
        while True:
            b = random.randint(0, self.buttcount-1)
            t = time()
            try:
                self.ws.send(f"/press_start {b}")
                self.ws.send(f"/press_end {b}")
            except Exception:
                await self.connect_loop("PRESS_BUTTON")
            r = random.randint(self.min_inte, self.max_inte)
            logging.info(f"PRESS_BUTTON: {b} OK ({time() - t}). next run in {r}")
            await asyncio.sleep(r)


class Heap(BaseAPI):
    async def action(self):
        while True:
            try:
                self.ws.send("/free_heap")
                heap = self.ws.recv().split(';')[1]
            except Exception as e:
                logging.info(f"FREE_HEAP: ERROR: {e}")
                await self.connect_loop("FREE_HEAP")
            t = datetime.now().strftime("%d-%m %H:%M:%S")
            with open('freeheap.txt', 'a') as f:
                f.write(f"{t},{heap}\n")
            logging.info(f"FREE HEAP:    {heap}")
            await asyncio.sleep(config.heap_interval)


def start_test():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        handlers=[
                            logging.FileHandler("log.txt"),
                            logging.StreamHandler()
                        ])
    w = Website(config.ip, config.buttons_count,
                config.min_interval, config.max_interval, config.heap_interval)
    p = Pult(config.ip, config.buttons_count,
             config.min_interval, config.max_interval, config.heap_interval)
    h = Heap(config.ip, config.buttons_count,
             config.min_interval, config.max_interval, config.heap_interval)
    loop = asyncio.new_event_loop()  # создаём новый асинхронный цикл
    loop.create_task(w.action())  # добавляем в него нашу функцию
    loop.create_task(p.action())  # добавляем в него нашу функцию
    loop.create_task(h.action())  # добавляем в него нашу функцию
    loop.run_forever()  # запускаем цикл


if __name__ == '__main__':
    start_test()
