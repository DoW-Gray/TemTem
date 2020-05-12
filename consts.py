# vim: set fileencoding=utf-8 :
"""
consts.py: access various constant TemTem data
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

from enum import Enum

from logging import error

TEMTEM_DATA = None
TEMTEM_CSV = 'temtem.csv'
ATTACK_DATA = None
ATTACK_CSV = 'attacks.csv'

class Stats(Enum):
    HP = 1
    Sta = 2
    Spe = 3
    Atk = 4
    Def = 5
    SpA = 6
    SpD = 7

class Types(Enum):
    Neutral = 1
    Fire = 2
    Water = 3
    Nature = 4
    Electric = 5
    Earth = 6
    Mental = 7
    Wind = 8
    Digital = 9
    Melee = 10
    Crystal = 10
    Toxic = 12

STAT_CONSTS = {
    Stats.HP: (80, 20_000, 15),
    Stats.Sta: (200, 25_000, 20),
    Stats.Spe: (100, 25_000, 10),
    Stats.Atk: (100, 25_000, 10),
    Stats.Def: (100, 25_000, 10),
    Stats.SpA: (100, 25_000, 10),
    Stats.SpD: (100, 25_000, 10),
}

TYPE_EFFECTIVENESS = {
    Types.Neutral: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 1.0,
        Types.Earth: 1.0,
        Types.Mental: 0.5,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 1.0,
    },
    Types.Fire: {
        Types.Neutral: 1.0,
        Types.Fire: 0.5,
        Types.Water: 0.5,
        Types.Nature: 2.0,
        Types.Electric: 1.0,
        Types.Earth: 0.5,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 2.0,
        Types.Toxic: 1.0,
    },
    Types.Water: {
        Types.Neutral: 1.0,
        Types.Fire: 2.0,
        Types.Water: 0.5,
        Types.Nature: 0.5,
        Types.Electric: 1.0,
        Types.Earth: 2.0,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 2.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 0.5,
    },
    Types.Nature: {
        Types.Neutral: 1.0,
        Types.Fire: 0.5,
        Types.Water: 2.0,
        Types.Nature: 0.5,
        Types.Electric: 1.0,
        Types.Earth: 2.0,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 0.5,
    },
    Types.Electric: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 2.0,
        Types.Nature: 0.5,
        Types.Electric: 0.5,
        Types.Earth: 0.5,
        Types.Mental: 2.0,
        Types.Wind: 2.0,
        Types.Digital: 2.0,
        Types.Melee: 1.0,
        Types.Crystal: 0.5,
        Types.Toxic: 1.0,
    },
    Types.Earth: {
        Types.Neutral: 1.0,
        Types.Fire: 2.0,
        Types.Water: 0.5,
        Types.Nature: 0.5,
        Types.Electric: 2.0,
        Types.Earth: 1.0,
        Types.Mental: 1.0,
        Types.Wind: 0.5,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 2.0,
        Types.Toxic: 1.0,
    },
    Types.Mental: {
        Types.Neutral: 2.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 1.0,
        Types.Earth: 1.0,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 2.0,
        Types.Crystal: 0.5,
        Types.Toxic: 1.0,
    },
    Types.Wind: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 0.5,
        Types.Earth: 1.0,
        Types.Mental: 1.0,
        Types.Wind: 0.5,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 2.0,
    },
    Types.Digital: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 1.0,
        Types.Earth: 1.0,
        Types.Mental: 2.0,
        Types.Wind: 1.0,
        Types.Digital: 2.0,
        Types.Melee: 2.0,
        Types.Crystal: 1.0,
        Types.Toxic: 1.0,
    },
    Types.Melee: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 1.0,
        Types.Earth: 2.0,
        Types.Mental: 0.5,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 0.5,
        Types.Crystal: 2.0,
        Types.Toxic: 1.0,
    },
    Types.Crystal: {
        Types.Neutral: 1.0,
        Types.Fire: 0.5,
        Types.Water: 1.0,
        Types.Nature: 1.0,
        Types.Electric: 2.0,
        Types.Earth: 0.5,
        Types.Mental: 2.0,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 1.0,
    },
    Types.Toxic: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 2.0,
        Types.Nature: 2.0,
        Types.Electric: 1.0,
        Types.Earth: 0.5,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 0.5,
        Types.Melee: 1.0,
        Types.Crystal: 0.5,
        Types.Toxic: 0.5,
    },
    None: {
        Types.Neutral: 1.0,
        Types.Fire: 1.0,
        Types.Water: 1.0,
        Types.Nature: 2.0,
        Types.Electric: 1.0,
        Types.Earth: 1.0,
        Types.Mental: 1.0,
        Types.Wind: 1.0,
        Types.Digital: 1.0,
        Types.Melee: 1.0,
        Types.Crystal: 1.0,
        Types.Toxic: 1.0,
    },
}

DEFAULT_LEVEL = 48

def load_temtem_data():
    from csv import DictReader
    global TEMTEM_DATA
    data = {}
    with open(TEMTEM_CSV, 'r') as fp:
        for row in DictReader(fp):
            base_stats = {}
            for stat in Stats:
                base_stats[stat] = int(row[stat.name])
            types = (row['Type 1'], row['Type 2'] or None)
            data[row['Name']] = (base_stats, types)

    # sanity checks
    if TEMTEM_DATA is not None:
        for tem in TEMTEM_DATA:
            if tem not in data:
                error('Lost data on %s when reloading base_stats.csv' % tem)

    TEMTEM_DATA = data

def load_attack_data():
    from csv import DictReader
    global ATTACK_DATA
    data = {}
    with open(ATTACK_CSV, 'r') as fp:
        for row in DictReader(fp):
            data[row['Name']] = row

    # sanity checks
    if ATTACK_DATA is not None:
        for attack in ATTACK_DATA:
            if attack not in data:
                error('Lost data on %s when reloading attacks.csv' % attack)

    ATTACK_DATA = data

def lookup_temtem_data(name):
    try:
        return TEMTEM_DATA[name]
    except (KeyError, TypeError):
        load_temtem_data()
        return TEMTEM_DATA[name]

def lookup_attack(name):
    try:
        return ATTACK_DATA[name]
    except (KeyError, TypeError):
        load_attack_data()
        return ATTACK_DATA[name]
