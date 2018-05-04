# Zinat

## About

This projects aims to create a simple to use self-hosted gallery app
with a minimal footprint in the server.

It is being built upon the following technologies:

* Python
* Falcon API framework
* peewee

Also is in the objectives of this project to create a decentralized social
network to share photos. Similar to instagram with the technology used at mastodon.

## License

Copyright (C) 2018-? Yábir García Benchakhtir (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see https://www.gnu.org/licenses/.


## Start services

### Start queue

  huey_consumer.py tasks.main.huey

### Start server
  ./start.sh

or

  uwsgi uwsgi.ini


### Start redis

  redis-server
