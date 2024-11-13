import random
import os
import socket
import time
import sys
import argparse

MINPORT = 60000

class MySender:
    
    #константа для максимального размера в байтах (8 ГБ)
    MAX_SIZE = 8 * 1024 * 1024 * 1024
    
    def __init__(self, ip: str):
        '''
        - конструктор, принимающий на вход реквизиты сервера для подключения
        
        ip - ip-адрес сервера для подключения
        port - порт сервера
        '''
        self.ip = ip
        #self.port = port
        
    def _generate_random_bytes(self) -> bytes:
        '''
        генерирует случайную последовательность байт размером до 8 ГБ
        '''
        
        #генерируем случайное число до 8 ГБ
        size = random.randint(1, MySender.MAX_SIZE)
        
        return os.urandom(size)
    
    def connect(self, port: int):
        '''
        создает tcp-соединение с переданным через конструктор сервером (в случае если соединение 
        установить не получилось из-за недоступности сервера, делается еще 2 попытки с интервалом 10с)
        и возвращает соединение
        '''
        
        #подключаемся к серверу
        for i in range(3):
            
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    print(f'Попытка подключения {i+1} к серверу {self.ip}:{port}')
                    s.connect((self.ip, port))
                    data_to_send = self._generate_random_bytes()
                    data_to_send = str(len(data_to_send)).encode() + data_to_send
                    s.sendall(data_to_send)
                    print(f'Отправлено {len(data_to_send)} байт')
                    break
                
            except (socket.error, ConnectionResetError) as e:
                    print(f'Попытка {i+1} подключения не удалась: {e}')
                    print(f'Повторная попытка через 10с')
                    time.sleep(10)
            
                    
        if i == 2:print(f'Превышено количество попыток подключения')
                
        
class MyListener:
    
    def __init__(self, ip: str, port: int):
        '''
        - конструктор, принимающий на вход реквизиты интерфейса на котором должен работать сервис
        
        ip - ip-адрес интерфейса
        port - порт интерфейса
        '''
        self.ip = ip
        self.port = port
        
    def _decode_data(self, data: bytes):
        print(f'Первые 16 байт данных: {data[:16].hex()}')
        print(f'Размер: {len(data)} байт')
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen()
            print(f'Сервис запущен на {self.ip}:{self.port}')
            while True:
                conn, addr = s.accept()
                with conn:
                    # Считываем длину данных
                    length_bytes = conn.recv(8)
                    data_length = int.from_bytes(length_bytes, 'big')
                    
                    # Получаем данные в зависимости от указанной длины
                    data = bytearray()
                    while len(data) < data_length:
                        packet = conn.recv(4096)
                        if not packet:
                            break
                        data.extend(packet)
                    
                    print(f'Получено {len(data)} байт')
                    self._decode_data(data)
                        
def main():
    global MINPORT
    
    parser = argparse.ArgumentParser(description='Программа для отправки и приема данных')
    #обязательный аргумент, который определяет роль приложения
    parser.add_argument('--role', choices=['send', 'recieve'], required=True, help='Роль приложения: send или recieve')
    
    #опциональные аргументы, которые требуются в зависимости от указанной роли
    parser.add_argument('--server', type=str, help='Имя сервера для отправки (если указана роль send)')
    parser.add_argument('--ip', type=str, help='Адрес сервера для прослушивания (если указана роль recieve)')
    parser.add_argument('--port', type=int, help='Порт сервера прослушивания (если указана роль recieve)')
    
    args = parser.parse_args()
    
    if args.role == 'send':
        print(f'Создаем приложение для отправки данных')
        if not args.server:
            print(f'Не указан адрес для отправки')
            sys.exit(1)
        sender = MySender(args.server)
        sender.connect(args.port if args.port else MINPORT)
        MINPORT += 1
        
    elif args.role == 'recieve':
        print(f'Создаем приложение для приема данных')
        print(f'Найденные аргументы: {args}')
        if not (args.ip or args.port):
            print(f'Не указан адрес для отправки')
            sys.exit(1)
        listener = MyListener(args.ip, args.port)
        listener.start()
        