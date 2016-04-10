import datetime
import time

# import click
import yaml

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler

from antminer_autotune.antminer import Antminer

default_config = {
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


def merge_dicts(*dict_args):
    """Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts."""
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def throttle(device: Antminer, job, idx,
             min_temp, max_temp,
             dec_time, inc_time,
             min_freq, max_freq,
             inc_step, dec_step, **kwargs):
    try:
        temperature = device.temperature
        elapsed = device.elapsed
        api_frequency = device.api_frequency
    except Exception as e:
        print('{:<16} -'.format(device.host), 'Failed to collect api data: ', e)
        return e

    print('{:<16} -'.format(device.host),
          'temp: {:>2}     '.format(temperature),
          'freq: {:>3}     '.format(api_frequency),
          'uptime: {:>8}'.format(elapsed))

    # TODO - Use settings from device.
    new_freq = None
    if temperature >= max_temp and elapsed > dec_time:  # cool-down logic
        if api_frequency > min_freq:
            new_freq = api_frequency - dec_step

    elif temperature <= min_temp and elapsed > inc_time:  # speed-up logic
        if api_frequency < max_freq:
            new_freq = api_frequency + inc_step

    if new_freq:
        job['job'].pause()
        print('{:<16} -'.format(device.host), 'setting frequency to:', new_freq)
        try:
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
    config = default_config.copy()
    miners = []

    try:
        config_file = yaml.load(open('config.yml'))
        config.update(config_file['defaults'])
        miners.extend(config_file['miners'])
    except FileNotFoundError:
        print('Config file was not found.')
        exit(1)
    except KeyError:
        print('Config file was malformed.')
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
