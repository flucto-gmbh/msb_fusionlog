import time
from datetime import (datetime, timezone, timedelta)
import sys, signal

def exit_handler(signal, frame):
    print(" byeeeee")
    sys.exit(0)


def calc_interval_from_timestamp(t : float, interval : int = 300):

    interval_minutes = interval/60

    # convert unix epoch to datetime object
    timestamp = datetime.fromtimestamp(t, timezone.utc)

    #create a new datetime object without the seconds
    timestamp_minutes = datetime(
        timestamp.year,
        timestamp.month,
        timestamp.day,
        timestamp.hour,
        timestamp.minute,
        tzinfo=timestamp.tzinfo,
    )

    # calculate the remaining minutes until the next interval is due 
    remaining_minutes = interval_minutes - (timestamp_minutes.minute % interval_minutes)

    # calculate the timestamp of the next interval
    next_interval = timestamp_minutes + timedelta(minutes=remaining_minutes)

    # convert the timestamp of the next interval to unix epoch
    return int(next_interval.strftime("%s"))

def get_next_interval(current_interval : int, interval : int = 300):
    return (current_interval + interval)

def main():
    signal.signal(signal.SIGINT, exit_handler)
    while True:
        current_interval_epoch = calc_interval_from_timestamp(time.time())
        current_interval_string = datetime.fromtimestamp(current_interval_epoch, timezone.utc)

        next_interval_epoch = get_next_interval(current_interval_epoch)
        next_interval_string = datetime.fromtimestamp(next_interval_epoch, timezone.utc)

        print(f'next interval: {current_interval_epoch} ({current_interval_string})')
        print(f'next interval: {next_interval_epoch} ({next_interval_string})')
        time.sleep(1)


if __name__ == "__main__":
    main()
