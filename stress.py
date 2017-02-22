import random
import argparse
import threading
import requests
import datetime

def now():
    return datetime.datetime.now()

def get_links(filename):
    with open(filename, 'r') as file:
        links = [line.strip() for line in file.readlines() if line.strip() != '']
    if not links:
        print("No links found")
        sys.exit(1)

    return links

print_lock = threading.Lock()
start_time = now()

def get(link):
    start_time = now()
    r = requests.get(link)
    end_time = now()
    kb = len(r.content) / 1024
    if kb > 1024:
        lenstr = "{0: 6.00f}MB".format(kb / 1024)
    else:
        lenstr = "{0: 6.00f}KB".format(kb)
    duration = end_time - start_time
    ms = duration.total_seconds() * 1000
    with print_lock:
        status = "{code: 3d} {time: 6.00f}ms {size} {link}".format(code=r.status_code,
                                                       size=lenstr, time=ms, link=link)
        print(status)

class GetterThread(threading.Thread):
    def __init__(self, links, running_time):
        super().__init__()
        self.links = links[:]
        self.running_time = running_time

    def run(self):
        while (now() - start_time).total_seconds() < self.running_time:
            link = random.choice(self.links)
            get(link)

def run_threads(num_threads, links, time):
    threads = []
    for i in range(num_threads):
        threads.append(GetterThread(links, time))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def main():
    parser = argparse.ArgumentParser(description='Stress test websites.')
    parser.add_argument('file', type=str,
                        help='a text file with one link per line')
    parser.add_argument('time', type=int,
                        help='number of seconds the threads work at submitting requests')
    parser.add_argument('threads', type=int,
                        help='number of threads used to send requests in parallel')
    
    args = parser.parse_args()

    links = get_links(args.file)
    print("Found", len(links), links)

    run_threads(args.threads, links, args.time)


main()

