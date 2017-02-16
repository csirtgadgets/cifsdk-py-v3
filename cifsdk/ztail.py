from cifsdk.client.http import HTTP as Client
import logging
import os.path
import select
import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from cifsdk.constants import CONFIG_PATH, REMOTE_ADDR, TOKEN, SEARCH_LIMIT, FORMAT, FEED_LIMIT, FEED_DAYS_LIMIT
from cifsdk.exceptions import AuthError
from csirtg_indicator.format import FORMATS
from cifsdk.utils import setup_logging, get_argument_parser, read_config
from csirtg_indicator import Indicator
from pprint import pprint
import arrow
from time import sleep
from csirtg_indicator.format.ztable import get_lines as get_lines_table
from csirtg_indicator.format.zcsv import get_lines as get_lines_csv

logger = logging.getLogger(__name__)



def main():
    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
            Env Variables:


            example usage:
                $ cif-tail
            '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-tail',
        parents=[p],
    )

    p.add_argument('--no-verify-ssl', help='turn TLS/SSL verification OFF', action='store_true')
    p.add_argument('--format', default='table')
    p.add_argument('--cycle', help='specify a cycle in which to run', default=5)
    p.add_argument('--filters', help='specify data filters to use', default='itype=ipv4,confidence=7,limit=10')
    p.add_argument('--remote', default=REMOTE_ADDR)
    p.add_argument('--token', default=TOKEN)
    p.add_argument('--start', default=arrow.get((arrow.utcnow().timestamp - 420)))

    args = p.parse_args()

    # setup logging
    setup_logging(args)

    verify_ssl = True
    if args.no_verify_ssl:
        verify_ssl = False

    filters = {}
    for k in args.filters.split(','):
        kk, v = k.split('=')
        filters[kk] = v

    remote = args.remote
    token = args.token
    client = Client(remote, token, verify_ssl=verify_ssl)

    start = args.start
    start = arrow.get(start)

    cycle = (int(args.cycle) * 60)

    # we want a 120s buffer for things that are being generated "now"
    end = arrow.get((arrow.utcnow().timestamp - 120))

    while True:
        logger.debug('now: %s' % arrow.utcnow())
        start = start.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        end = end.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

        filters['reporttime'] = '{},{}'.format(start, end)
        logger.debug('searching {} - {}'.format(start, end))
        resp = client.indicators_search(filters)
        if args.format == 'csv':
            for l in get_lines_csv(resp):
                print(l)
        else:
            for l in get_lines_table(resp):
                print(l)

        logger.debug('sleeping for {}m'.format(args.cycle))
        sleep(cycle)
        start = arrow.get(arrow.get(end).timestamp + 1)
        end = arrow.get((arrow.utcnow().timestamp - 120))

if __name__ == '__main__':
    main()
