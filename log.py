#!/usr/bin/env python

from sys import stdin

from ua_parser import user_agent_parser

from apache import parse_apache, parse_apache_date

from geoip2.database import Reader

from influxdb import InfluxDBClient

geoip = Reader('GeoLite2-City.mmdb')


def geo_ip(line):
    if 'ip_address' in line:
        r = geoip.city(line['ip_address'])
        line['country_code'] = r.country.iso_code
    return line


def user_agent(line):
    if 'client' in line:
        line['client'] = user_agent_parser.Parse(line['client'])
    return line


def time(line):
    line['time'] = parse_apache_date(line['timestamp'])
    return line


if __name__ == '__main__':
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'otto')
    #client.create_database('otto')

    columns = ['time', 'country_code', 'response_code', 'ip_address', 'path']
    for line in stdin.readlines():
        if line.strip() == "":
            continue
        try:
            line = time(geo_ip(user_agent(parse_apache(line))))
            shmurtz = dict(name='otto',
                       columns=columns,
                       points=[[line.get(c, None) for c in columns]])
            client.write_points(data=[ shmurtz ], batch_size=100)
        except Exception as e:
            print line
            print e
        pass
