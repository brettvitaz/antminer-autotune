import json
import os
import re
import socket
import time
from collections import OrderedDict
from pathlib import Path, PosixPath

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from antminer_autotune.util import makedir, fix_json_format
from antminer_autotune.models import models
from antminer_autotune.util import merge_dicts


def ssh_client(fn):
    def fn_wrap(self, *args, **kwargs):
        with SSHClient() as client:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy)
            client.connect(self.host, self.ssh_port, self._username, self._password)
            return fn(self, client, *args, **kwargs)

    return fn_wrap


def api_cache(key, cache_time=1):
    def api_cache_wrap(fn):
        def fn_wrap(self, *args, **kwargs):
            try:
                if self._api_cache[key]['timestamp'] + cache_time > time.time():
                    return self._api_cache['stats']['result']
            except KeyError:
                pass
            self._api_cache[key] = {
                'result': fn(self, *args, **kwargs),
                'timestamp': time.time()
            }
            return self._api_cache['stats']['result']

        return fn_wrap

    return api_cache_wrap


class Antminer:
    CONFIG_FILE_DIR = '/config'
    CONFIG_FILE_NAME = 'cgminer.conf'
    RESTART_COMMAND = '/etc/init.d/cgminer.sh restart'
    TIMEOUT = 5

    def __init__(self, host, model, ssh_port=None, api_port=None, username=None, password=None, **kwargs):
        if isinstance(model, str):
            self.model = models[model].copy()
        elif isinstance(model, dict):
            self.model = model.copy()
        else:
            raise TypeError('Arg `model` must be a string (key from known models dict) or a dict.')
        self.model = merge_dicts(self.model, kwargs)

        self.host = host
        self.ssh_port = int(ssh_port or self.model['ssh_port'])
        self.api_port = int(api_port or self.model['api_port'])
        self._username = username or self.model['username']
        self._password = password or self.model['password']

        self._local_config_path = Path(host, self.CONFIG_FILE_NAME)
        self._remote_config_path = PosixPath(self.CONFIG_FILE_DIR, self.CONFIG_FILE_NAME)

        self._config = None  # self.read_config()
        self._api_cache = {}

    @property
    def config(self):
        if not self._config:
            self._config = self.read_config()
        return self._config

    @property
    def frequency(self):
        return int(self.config['bitmain-freq'])

    @frequency.setter
    def frequency(self, value):
        if self._is_valid_frequency(int(value)):
            self.config['bitmain-freq'] = str(value)
        else:
            raise ValueError('Frequency is not valid: {}'.format(value))

    def _is_valid_frequency(self, value):
        return value in (v.value for v in self.model['frequencies'])

    @property
    def fan_speed(self):
        return self.config['bitmain-fan-pwm']

    @fan_speed.setter
    def fan_speed(self, value):
        if self._is_valid_fan_speed(int(value)):
            self.config['bitmain-fan-pwm'] = str(value)
        else:
            raise ValueError('Fan speed is not valid:'.format(value))

    def _is_valid_fan_speed(self, value):
        return 0 <= value <= 100

    @property
    def fan_control(self):
        return self.config['bitmain-fan-ctrl']

    @fan_control.setter
    def fan_control(self, value):
        if isinstance(value, bool):
            self.config['bitmain-fan-ctrl'] = value

    @property
    @api_cache('stats')
    def stats(self):
        return self.send_api_command({'command': 'stats'})['STATS'][1]

    @property
    def temperature(self):
        """Find and return the highest hashing board temperature from api 'stats' call.

        :return: highest temperature of hashing boards
        """
        return max([v for k, v in self.stats.items() if re.fullmatch('temp\d+', k)])

    @property
    def hash_rate_avg(self):
        return self.stats['GHS av']

    @property
    def hash_rate_5s(self):
        return self.stats['GHS 5s']

    @property
    def hardware_error_rate(self):
        return self.stats['Device Hardware%']

    @property
    def api_frequency(self):
        return int(self.stats['frequency'])

    @property
    @api_cache('summary')
    def summary(self):
        return self.send_api_command({'command': 'summary'})['SUMMARY'][0]

    @property
    def elapsed(self):
        return int(self.summary['Elapsed'])

    @ssh_client
    def pull_config(self, client):
        makedir(self.host)
        scp = SCPClient(client.get_transport())
        scp.get(str(self._remote_config_path), str(self._local_config_path))
        os.chmod(str(self._local_config_path), 0o777)

    @ssh_client
    def push_config(self, client, restart=False):
        self.write_config()

        scp = SCPClient(client.get_transport())
        scp.put(str(self._local_config_path), str(self._remote_config_path))
        if restart:
            client.exec_command(self.RESTART_COMMAND)
            time.sleep(10)

    def read_config(self, from_local=False):
        if not from_local:
            self.pull_config()
        with open(str(self._local_config_path)) as f:
            conf = json.loads(f.read(), object_pairs_hook=OrderedDict)

        return conf

    def reset_config(self):
        self._config = None

    def write_config(self):
        if not self._config:
            raise RuntimeError('Config has not been read from device.')
        with open(str(self._local_config_path), 'w') as f:
            f.write(json.dumps(self._config, indent=0))

    def send_api_command(self, cmd, expect_response=True):
        resp = None

        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as _socket:
            _socket.settimeout(self.TIMEOUT)
            _socket.connect((self.host, self.api_port))
            _socket.send(json.dumps(cmd).encode())

            if expect_response:
                resp = b''
                while True:
                    buf = _socket.recv(4096)
                    if buf:
                        resp += buf
                    else:
                        break

                resp = json.loads(fix_json_format(resp.decode()))

        return resp
