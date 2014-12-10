import re
import time


APACHE = re.compile(r'^(?P<ip_address>\S+) - (?P<requesting_user>\S+) +\[(?P<timestamp>.*?)\] ("-"|("(?P<method>\w+) +(?P<request>\S+)( +HTTP/(?P<http_version>[0-9.]+))?")) (?P<response_code>\d{3}) (-|(?P<size>\d+)) "(?P<referrer>[^"]*)" "(?P<client>[^"]*)"')

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


def parse_apache_date(txt):
    txt, tz = txt.split(' ')
    dmy, h, m, s = txt.split(':')
    d, M, y = dmy.split('/')
    M = MONTHS.index(M) + 1
    return int(time.mktime((int(y), M, int(d), int(h), int(m), int(s), -1, -1, -1)))

def parse_apache(line):
    return _parse(APACHE, line)


# Stolen from http://tech.yipit.com/2012/08/03/parsible-straightforward-log-parsing/
def _parse(regex, line):
    r = regex.search(line)
    result_set = {}
    if r:
        for k, v in r.groupdict().iteritems():
            # Normalize our data
            if v is None or v == "-":
                continue
            # Make the dictionary fields a bit more useful
            if k == "request":
                if "?" in v:
                    result_set["path"], _, result_set["query"] = v.partition("?")
                else:
                    result_set["path"] = v
            else:
                result_set[k] = v
    else:
        print "Error: ", line
        #raise Exception(line)
    return result_set


if __name__ == '__main__':
    lines = [
        '183.15.4.245 - - [08/Dec/2014:17:54:01 +0100] "-" 408 - "-" "-"',
        '82.66.246.250 - tracsearch [09/Dec/2014:16:06:34 +0100] "GET /?q=debian&start=&end=&facet_status=&facet__type=&facet_component=&facet_domain=&facet_priority=&facet_user=vschmitt&facet_keywords=&facet_path= HTTP/1.1" 200 7715 "https://search.bearstech.com/?q=debian&start=&end=" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0"'
    ]
    p = parse_apache(lines[0])
    print p
    assert p['timestamp'] is not None
    p = parse_apache(lines[1])
    print p
    assert p['requesting_user'] == 'tracsearch'
    print parse_apache_date('09/Dec/2014:16:06:34 +0100')

