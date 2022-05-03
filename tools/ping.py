#!/usr/bin/python3
# -*- coding: utf-8 -*-

from threading import Thread
from os import name, system
from time import sleep

IP_ROOT: str = "192.168.1"  # IPV4 Root
OPTION, NULL = ("-n", "NUL") if name == "nt" else ("-c", "/dev/null")
DELAY_FRAME = .1  # Time between two frame of loading

if __name__ == "__main__":

    loaded: int = 0
    results: list = []

    def ping(ip: str):
        global results, loaded
        if system(f"ping {OPTION} 1 {ip} > {NULL}") == 0:
            results.append(ip)
        loaded += 1

    def _loading():

        while loaded < 254:
            print(
                f"Processing {round(loaded * 100 / 256)}%", end='\r')
            sleep(DELAY_FRAME)

        print(f"\n{len(results)} IPV4 found:")
        for ip in results:
            print(f"    {ip}")

    Thread(target=_loading).start()

    threads = [Thread(target=ping, args=(
        f"{IP_ROOT}.{host}",)) for host in range(1, 255)]

    for p in threads:
        p.start()

    for p in threads:
        p.join()
