from antminer_control.antminer import Antminer
from apscheduler.schedulers.blocking import BlockingScheduler

miners = [
    Antminer('192.168.168.13'),
    Antminer('192.168.168.194')
]


def throttle(device):
    print(device._host, 'temp:', device.temperature, device.elapsed)
    temp = device.temperature
    if temp > 70 and device.elapsed > 30:
        new_freq = device.api_frequency - 25
        print(device._host, 'lowering freq to:', new_freq)
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
