#!/usr/bin/env python3.8
# vim: set fileencoding=utf-8 :
"""
wiki_tems_scraper.py: Scrape moveset and trait data from the wiki
Copyright (C) 2020 DoW

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import os

from urllib.request import urlopen
from html.parser import HTMLParser
from contextlib import suppress
from time import sleep
import yaml

sys.path.append('..')  # I'm pretty sure there's a better way to do this
import static  # noqa: E402

os.chdir('..')

OUT_FILE = os.path.join('data', 'temtem.yaml')

LEARN_TYPE_LOOKUP = {
    'by Leveling\n': 'Level Up',
    'through Technique Courses\n': 'TC',
    'through Breeding\n': 'Egg',
}


class WikiParser(HTMLParser):

    def __init__(self):
        self._state = 'start'
        self._learn_type = None
        self.tem_data = {}
        self._attack_names = []
        self.current_tem = None

        self._populate_data()

        super().__init__()

    def _populate_data(self):
        self.tem_data = raw_tem_data()
        for tem in self.tem_data.values():
            tem['Traits'] = []
            tem['Moves'] = {'Level Up': [], 'TC': [], 'Egg': []}
        static.load_attack_data()
        self._attack_names = list(static.ATTACK_DATA.keys())

    @property
    def this_tem(self):
        return self.tem_data[self.current_tem]

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and self._state == 'Moves':
            with suppress(IndexError):
                move = [attr[1] for attr in attrs if attr[0] == 'title'][0]
                if move in self._attack_names:
                    self.this_tem['Moves'][self._learn_type].append(move)

    def handle_data(self, data):
        if data == 'Traits':
            self._state = 'Traits'
        elif self._state == 'Traits' and data.strip():
            self.this_tem['Traits'].append(data)
        elif data.strip().startswith('List of Techniques'):
            self._state = 'Moves'
            self._learn_type = LEARN_TYPE_LOOKUP[data.split('Learns ')[1]]

    def handle_endtag(self, tag):
        if tag == 'td' and self._state == 'Traits':
            self._state = None
        elif tag == 'table' and self._state == 'Moves':
            self._state = None


def raw_tem_data():
    from csv import DictReader

    tem_csv = os.path.join('data', 'temtem.csv')
    data = {}
    with open(tem_csv, 'r') as fp:
        for row in DictReader(fp):
            data[row['Name']] = row

    return data


def main(argv):
    if len(argv) > 1:
        out_file = argv[1]
    else:
        out_file = 'temtem.yaml'
    print(f'Will output data to {out_file}')

    parser = WikiParser()
    for tem in parser.tem_data:
        print(f'Reading webpage for {tem}')
        parser.current_tem = tem
        parser.feed(
            urlopen(f'https://temtem.gamepedia.com/{tem}').read().decode('utf-8')
        )

        sleep(1)  # Don't accidentally DoS the wiki

    print(f'Printing data to {out_file}')
    with open(out_file, 'w') as fp:
        print(yaml.dump(parser.tem_data, indent=4), file=fp)


if __name__ == '__main__':
    main(sys.argv)
