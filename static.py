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

import os

from enum import Enum
import yaml

from log import error

TEMTEM_DATA = None
TEMTEM_YAML = os.path.join('data', 'temtem.yaml')
ATTACK_DATA = None
ATTACK_YAML = os.path.join('data', 'attacks.yaml')


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


class Statuses(Enum):
    cold = 1
    frozen = 2
    asleep = 3
    trapped = 4
    doomed = 5
    seized = 6
    poisoned = 7
    burned = 8
    exhausted = 9
    vigorized = 10
    immune = 11
    regenerated = 12
    nullified = 13
    evading = 14
    alerted = 15
    exiled = 16


STAT_CONSTS = {
    # used in stat calculation
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

DEFAULT_LEVEL = 58


def load_temtem_data():
    global TEMTEM_DATA
    with open(TEMTEM_YAML, 'r') as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)
    for tem, tem_data in data.items():
        tem_data['Stats'] = {}
        for stat in Stats:
            tem_data['Stats'][stat] = tem_data[stat.name]
            del tem_data[stat.name]
        t1 = tem_data['Type 1']
        t2 = tem_data['Type 2']
        tem_data['Types'] = (Types[t1], Types[t2] if t2 else None)
        del tem_data['Type 1']
        del tem_data['Type 2']
        tem_data['Traits'] = tuple(tem_data['Traits'])

    # sanity checks
    if TEMTEM_DATA is not None:
        for tem in TEMTEM_DATA:
            if tem not in data:
                error(f'Lost data on {tem} when reloading {TEMTEM_YAML}')

    TEMTEM_DATA = data


def load_attack_data():
    from effects import Effect

    global ATTACK_DATA

    def gen_effect_dict(effects):
        tmp_dict = {}
        for key, value in effects.items():
            try:
                tmp_dict[Stats[key]] = value
            except KeyError:
                try:
                    tmp_dict[Statuses[key]] = value
                except KeyError:
                    tmp_dict[key] = value
        return tmp_dict

    with open(ATTACK_YAML, 'r') as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)

    for attack, atk_data in data.items():
        atk_data['name'] = attack
        atk_data['type'] = Types[atk_data['type']]
        if 'synergy type' in atk_data:
            atk_data['synergy type'] = Types[atk_data['synergy type']]

        if 'damage' not in atk_data:
            atk_data['damage'] = 0

        atk_data['effects'] = Effect(
            attacker=gen_effect_dict(atk_data.get('self', {})),
            target=gen_effect_dict(atk_data.get('effects', {})),
        )

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
def test_lookup_temtem():
    from test_data import GYALIS_DATA, PIGEPIC_DATA

    for test_data, name in (GYALIS_DATA, 'Gyalis'), (PIGEPIC_DATA, 'Pigepic'):
        tem_data = lookup_temtem_data(name)
        for key, value in test_data.items():
            assert tem_data[key] == value


def test_lookup_attack():
    from test_data import BETA_BURST_DATA, HIGHPRESSURE_WATER_DATA, STONE_WALL_DATA

    assert lookup_attack('Beta Burst') == BETA_BURST_DATA
    assert lookup_attack('High-pressure Water') == HIGHPRESSURE_WATER_DATA
    assert lookup_attack('Stone Wall') == STONE_WALL_DATA
