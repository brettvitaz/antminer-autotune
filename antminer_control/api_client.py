import json
import socket
import time

from collections import namedtuple

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

adr = namedtuple('Address', 'host port')

HOST = '192.168.168.13'

SSH_PORT = 22
API_PORT = 4028

SSH_ADDRESS = adr(HOST, SSH_PORT)
API_ADDRESS = adr(HOST, API_PORT)

TIMEOUT = 5

CGMINER_STATS = {
    'command': 'stats'
}

CGMINER_RESTART = {
    'command': 'restart'
}

CGMINER_DETAILS = {
    'command': 'devdetails'
}


def send_command(cmd):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as _socket:
        _socket.settimeout(TIMEOUT)
        _socket.connect(API_ADDRESS)
        _socket.send(json.dumps(cmd).encode())

        resp = b''
        while True:
            buf = _socket.recv(4096)
            if buf:
                resp += buf
            else:
                break
    return resp


def get_stats(stats):
    return stats['STATS'][1]


def get_temps(stats):
    return {k: v for k, v in stats.items() if k.startswith('temp')}


def check_temps(stats):
    temps = get_temps(get_stats(stats))
    return max(temps.values())


def fix_json_format(bad_json: str):
    return bad_json.replace('}{', '},{').strip(' \0')


def createSSHClient(server, port, user, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def retrieve_config(path, address):
    with SSHClient() as client:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(address.host, address.port, 'root', 'admin')
        scp = SCPClient(client.get_transport())
        scp.get('/config/cgminer.conf', path)


def send_config(path, address):
    with SSHClient() as client:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(address.host, address.port, 'root', 'admin')
        scp = SCPClient(client.get_transport())
        scp.put(path, '/config/cgminer.conf')
        print(client.exec_command('/etc/init.d/cgminer.sh restart'))
        time.sleep(10)


# try:
#     send_config('./test.conf', SSH_ADDRESS)
# except Exception as e:
#     print(e)
#     exit(1)

# try:
#     retrieve_config('./config.conf', SSH_ADDRESS)
# except Exception as e:
#     print(e)
#     exit(1)

# print(json.loads(fix_json_format(send_command(CGMINER_DETAILS).decode())))

for i in range(1200):
    time.sleep(1)
    try:
        stats = json.loads(fix_json_format(send_command(CGMINER_STATS).decode()))
        stats = check_temps(stats)

    except (socket.timeout, ConnectionRefusedError, ConnectionResetError) as e:
        print(i, str(e))
        continue
    print(i, stats)
