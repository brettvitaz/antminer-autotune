import json
import sys

from antminer_autotune.antminer import Antminer, models

if __name__ == '__main__':
    print(sys.argv)

    if len(sys.argv) < 3:
        print('Usage:')
        print('python quick_config.py model host [ssh_port] [username] [password]')
        print('')
        print('    model - {}'.format(list(models.keys())))
        print('')
        print('Note: defaults will be used for omitted optional arguments, but if you need ')
        print('to specify a later argument, you must also specify the preceding arguments.')
        exit(1)

    if sys.argv[1] not in models:
        print('Unknown model: {}'.format(sys.argv[0]))
        exit(1)

    args = ['model', 'host', 'ssh_port', 'username', 'password']

    config = {args[i]: v for i, v in enumerate(sys.argv[1:])}

    device = Antminer(**config)

    # device._config = device.read_config(True)

    opt = input('Fan control [{}]: '.format(device.fan_control))
    if opt:
        device.fan_control = opt.lower() in ['true', 't', 'yes', 'y', '1']

    opt = input('Fan speed [{}]: '.format(device.fan_speed))
    if opt:
        device.fan_speed = opt

    opt = input('Frequency [{}]: '.format(device.frequency))
    if opt:
        device.frequency = opt

    print('\nNew config:')
    print(json.dumps(device.config, indent=2))

    opt = input('\nPush new config? [y/N]: ')
    if opt and opt.lower() in ['yes', 'y']:
        print('Pushing config...')
        device.push_config(restart=True)
        print('Done.')
