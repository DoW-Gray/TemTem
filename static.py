# vim: set fileencoding=utf-8 :
"""
static.py: access various static TemTem data
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

from log import error

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
    neutral = 1
    fire = 2
    water = 3
    nature = 4
    electric = 5
    earth = 6
    mental = 7
    wind = 8
    digital = 9
    melee = 10
    crystal = 11
    toxic = 12


STAT_CONSTS = {
    Stats.HP: (80, 20_000, 15),
    Stats.Sta: (200, 25_000, 20),
    Stats.Spe: (100, 25_000, 10),
    Stats.Atk: (100, 25_000, 10),
    Stats.Def: (100, 25_000, 10),
    Stats.SpA: (100, 25_000, 10),
    Stats.SpD: (100, 25_000, 10),
}

# lookup table: TE[attack][target] = effectiveness
TYPE_EFFECTIVENESS = {
    Types.neutral: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 1.0,
        Types.earth: 1.0,
        Types.mental: 0.5,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 1.0,
        Types.toxic: 1.0,
    },
    Types.fire: {
        Types.neutral: 1.0,
        Types.fire: 0.5,
        Types.water: 0.5,
        Types.nature: 2.0,
        Types.electric: 1.0,
        Types.earth: 0.5,
        Types.mental: 1.0,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 2.0,
        Types.toxic: 1.0,
    },
    Types.water: {
        Types.neutral: 1.0,
        Types.fire: 2.0,
        Types.water: 0.5,
        Types.nature: 0.5,
        Types.electric: 1.0,
        Types.earth: 2.0,
        Types.mental: 1.0,
        Types.wind: 1.0,
        Types.digital: 2.0,
        Types.melee: 1.0,
        Types.crystal: 1.0,
        Types.toxic: 0.5,
    },
    Types.nature: {
        Types.neutral: 1.0,
        Types.fire: 0.5,
        Types.water: 2.0,
        Types.nature: 0.5,
        Types.electric: 1.0,
        Types.earth: 2.0,
        Types.mental: 1.0,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 1.0,
        Types.toxic: 0.5,
    },
    Types.electric: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 2.0,
        Types.nature: 0.5,
        Types.electric: 0.5,
        Types.earth: 0.5,
        Types.mental: 2.0,
        Types.wind: 2.0,
        Types.digital: 2.0,
        Types.melee: 1.0,
        Types.crystal: 0.5,
        Types.toxic: 1.0,
    },
    Types.earth: {
        Types.neutral: 1.0,
        Types.fire: 2.0,
        Types.water: 0.5,
        Types.nature: 0.5,
        Types.electric: 2.0,
        Types.earth: 1.0,
        Types.mental: 1.0,
        Types.wind: 0.5,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 2.0,
        Types.toxic: 1.0,
    },
    Types.mental: {
        Types.neutral: 2.0,
        Types.fire: 1.0,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 1.0,
        Types.earth: 1.0,
        Types.mental: 1.0,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 2.0,
        Types.crystal: 0.5,
        Types.toxic: 1.0,
    },
    Types.wind: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 0.5,
        Types.earth: 1.0,
        Types.mental: 1.0,
        Types.wind: 0.5,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 1.0,
        Types.toxic: 2.0,
    },
    Types.digital: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 1.0,
        Types.earth: 1.0,
        Types.mental: 2.0,
        Types.wind: 1.0,
        Types.digital: 2.0,
        Types.melee: 2.0,
        Types.crystal: 1.0,
        Types.toxic: 1.0,
    },
    Types.melee: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 1.0,
        Types.earth: 2.0,
        Types.mental: 0.5,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 0.5,
        Types.crystal: 2.0,
        Types.toxic: 1.0,
    },
    Types.crystal: {
        Types.neutral: 1.0,
        Types.fire: 0.5,
        Types.water: 1.0,
        Types.nature: 1.0,
        Types.electric: 2.0,
        Types.earth: 0.5,
        Types.mental: 2.0,
        Types.wind: 1.0,
        Types.digital: 1.0,
        Types.melee: 1.0,
        Types.crystal: 1.0,
        Types.toxic: 1.0,
    },
    Types.toxic: {
        Types.neutral: 1.0,
        Types.fire: 1.0,
        Types.water: 2.0,
        Types.nature: 2.0,
        Types.electric: 1.0,
        Types.earth: 0.5,
        Types.mental: 1.0,
        Types.wind: 1.0,
        Types.digital: 0.5,
        Types.melee: 1.0,
        Types.crystal: 0.5,
        Types.toxic: 0.5,
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
            t1 = row['Type 1']
            t2 = row['Type 2']
            types = (Types[t1], Types[t2] if t2 else None)
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
            res = {}
            for col, cell in row.items():
                if col in ('DMG', 'STA', 'Hold', 'Priority'):
                    res[col] = 0 if cell == '-' else int(cell)
                elif col.endswith('Type'):
                    res[col] = Types[cell] if cell else None
                else:
                    res[col] = cell
            data[row['Name']] = res

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


# Tests
def test_load_temtem_data():
    from test_data import GYALIS_DATA, PIGEPIC_DATA

    load_temtem_data()

    assert TEMTEM_DATA['Gyalis'] == GYALIS_DATA
    assert TEMTEM_DATA['Pigepic'] == PIGEPIC_DATA


def test_load_attack_data():
    from test_data import BETA_BURST_DATA, HIGHPRESSURE_WATER_DATA, STONE_WALL_DATA

    load_attack_data()

    assert ATTACK_DATA['Beta Burst'] == BETA_BURST_DATA
    assert ATTACK_DATA['High-pressure Water'] == HIGHPRESSURE_WATER_DATA
    assert ATTACK_DATA['Stone Wall'] == STONE_WALL_DATA


def test_lookup_temtem():
    from test_data import GYALIS_DATA, PIGEPIC_DATA

    assert lookup_temtem_data('Gyalis') == GYALIS_DATA
    assert lookup_temtem_data('Pigepic') == PIGEPIC_DATA


def test_lookup_attack():
    from test_data import BETA_BURST_DATA, HIGHPRESSURE_WATER_DATA, STONE_WALL_DATA

    assert lookup_attack('Beta Burst') == BETA_BURST_DATA
    assert lookup_attack('High-pressure Water') == HIGHPRESSURE_WATER_DATA
    assert lookup_attack('Stone Wall') == STONE_WALL_DATA
