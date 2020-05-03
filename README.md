# pwnloris
An improved slowloris DOS tool which keeps attacking until the server starts getting exhausted.


## Detailed info

This tool abuses the *CVE-2007-6750* and *CVE-2012-5568* vulnerabilities. The exploits works by using just one machine by creating multiple threads and sending from each thread incomplete requests while keeping the connections alive thus using up all the resources of the server and making the website unreachable.


## Usage

This tool has only one required argument being the host and optionally with a port e.g:

    $ ./pwnloris.py example.com
    $ ./pwnloris.py 192.168.2.42:443


Optional arguments to be passed:

- **-h, --help**      show this help message and exit
- **-t, --tor** enable to attack through TOR
- **-n [THREADS]**    number of threads (default 8)
- **-k [KEEPALIVE]**  seconds to keep connection alive (default 90)
- **-i [INTERVAL]**   seconds between keep alive check intervals (default 5)
- **-sh [SOCKSHOST]**  host TOR is running (default 127.0.0.1)
- **-sp [SOCKSPORT]**  port TOR is using (default 9050)

All the options could be used as example: an attack on 192.168.2.42 on port 8080 without TOR using 16 threads, 120 seconds keeping the connection alive and a keep-alive check of every 10 seconds:

    $ ./pwnloris.py 192.168.2.42:8080 -n 16 -k 120 -i 10

## Installation

The tool uses `pysocks` for the capability to route through TOR and `argparse` for the arguments obviously. These can be installed with the following command:

    $ pip install -r requirements.txt

Besides the packages it's also important to have TOR installed and running on your machine. You can install TOR in different ways depending on your operating system and after installing run TOR as a daemon/background process.
