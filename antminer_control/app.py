from antminer_control.antminer import Antminer
from apscheduler.schedulers.blocking import BlockingScheduler

miners = [
    Antminer('192.168.168.13'),
    Antminer('192.168.168.194')
]


def throttle(device: Antminer):
    temperature = device.temperature
    elapsed = device.elapsed

    print(device.host, 'temp:', temperature, elapsed)

    new_freq = None
    if temperature > 75 and elapsed > 30:
        if device.api_frequency > 100:  # cool-down logic
            new_freq = device.api_frequency - 25

    elif temperature < 69 and elapsed > 600:
        if device.api_frequency < 700:  # speed-up logic
            new_freq = device.api_frequency + 25

    if new_freq:
        print(device.host, 'changing freq to:', new_freq)
        device.frequency = new_freq
        device.push_config(True)


if __name__ == '__main__':
    scheduler = BlockingScheduler()

    for miner in miners:
        scheduler.add_job(throttle, 'interval', args=(miner,), seconds=5)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
