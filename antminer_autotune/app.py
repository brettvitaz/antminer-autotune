import datetime
import time

# import click
import sys
import yaml

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler

from antminer_autotune.antminer import Antminer
from antminer_autotune.util import merge_dicts

DEFAULT_CONFIG = {
    'min_temp': 72,
    'max_temp': 76,
    'dec_time': 30,
    'inc_time': 900,
    'dec_step': 25,
    'inc_step': 25,
    'min_freq': 100,
    'max_freq': 700,
    'refresh_time': 5
}

DEFAULT_CONFIG_FILENAME = 'config.yml'


def throttle(device, job, idx,
             min_temp, max_temp,
             dec_time, inc_time,
             min_freq, max_freq,
             inc_step, dec_step, **kwargs):
    """

    :type device: Antminer
    :type job: apscheduler.Job
    """
    try:
        temperature = device.temperature
        elapsed = device.elapsed
        api_frequency = device.api_frequency
        hw_err = device.hardware_error_rate
    except Exception as e:
        print('{:<16} -'.format(device.host), 'Failed to collect api data: ', e)
        return e

    print('{:<16} -'.format(device.host),
          'temp: {:>2}     '.format(temperature),
          'freq: {:>3}     '.format(api_frequency),
          'uptime: {:>6}   '.format(elapsed),
          'hr: {:>7.2f}   '.format(device.hash_rate_avg), 
          'h5: {:>7.2f}   '.format(device.hash_rate_5s), 
          'hw: {:>7.4}%'.format(hw_err))

    # TODO - Use settings from device.
    new_freq = None
    if api_frequency > device.model['max_freq']:
        new_freq = device.model['max_freq']

    elif temperature > max_temp and elapsed > dec_time:  # cool-down logic
        if api_frequency > device.model['min_freq']:
            new_freq = device.prev_frequency()

    elif api_frequency < device.model['max_freq'] and temperature < min_temp and elapsed > inc_time:  # speed-up logic
        if api_frequency < device.model['max_freq']:
            new_freq = device.next_frequency()

    if new_freq:
        job['job'].pause()
        print('{:<16} -'.format(device.host), 'setting frequency to:', new_freq)
        try:
            device.reset_config()
            device.frequency = new_freq
            device.push_config(True)
            time.sleep(15)
        except Exception as e:  # TODO - Investigate possible failures and retry options.
            print('{:<16} -'.format(device.host), 'failed to set frequency!', e)
        job['job'].resume()


def listener(event):
    print(event)
    print(event.exception)


# TODO - Click doesn't work easily on Python 3. Investigate alternative cli library.
# @click.command()
# @click.option('--config', type=click.File())
def main(*args, **kwargs):
    config_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG_FILENAME
    config = DEFAULT_CONFIG.copy()
    miners = []

    try:
        config_file = yaml.load(open(config_filename))
        config.update(config_file['defaults'])
        miners.extend(config_file['miners'])
    except FileNotFoundError:
        print('Config file \'{}\' was not found.'.format(config_filename))
        exit(1)
    except KeyError as e:
        print('Config did not contain section {}.'.format(e))
        exit(1)

    # print(config)
    # print(miners)

    scheduler = BlockingScheduler(job_defaults={'coalesce': True})
    scheduler.add_listener(listener, EVENT_JOB_ERROR)

    for idx, miner in enumerate(miners):
        job_config = merge_dicts(config, {'job': {}, 'idx': idx})
        job = scheduler.add_job(throttle, 'interval', args=((Antminer(**miner)),), kwargs=job_config,
                                misfire_grace_time=30, seconds=config['refresh_time'],
                                next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=idx * 0.2))
        job_config['job'].update({'job': job})

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
