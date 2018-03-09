## Slowloris DOS Attack

This script abuses the CVE-2007-6750 vulnerability. This exploits works using just one machine by creating multiple threads and sending from each thread incomplete requests while keeping the collection alive thus using up all the resources of the server and making the website unreachable.


### Usage
    $ ./slowloris.py host:port {-t/--tor}
