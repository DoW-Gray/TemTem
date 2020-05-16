# vim: set fileencoding=utf-8 :
"""
test_data.py: data imported for unit tests
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

# For static.py
from static import Stats, Types

GYALIS_DATA = (
    {
        Stats.HP: 86,
        Stats.Sta: 44,
        Stats.Spe: 100,
        Stats.Atk: 85,
        Stats.Def: 61,
        Stats.SpA: 23,
        Stats.SpD: 61,
    },
    (Types.crystal, Types.melee),
)
PIGEPIC_DATA = (
    {
        Stats.HP: 54,
        Stats.Sta: 72,
        Stats.Spe: 58,
        Stats.Atk: 60,
        Stats.Def: 72,
        Stats.SpA: 45,
        Stats.SpD: 72,
    },
    (Types.wind, None),
)
BETA_BURST_DATA = {
    'Name': 'Beta Burst',
    'Type': Types.mental,
    'Synergy Type': None,
    'Class': 'Special',
    'DMG': 100,
    'STA': 23,
    'Hold': 0,
    'Priority': 2,
}
HIGHPRESSURE_WATER_DATA = {
    'Name': 'High-pressure Water',
    'Type': Types.water,
    'Synergy Type': Types.fire,
    'Class': 'Special',
    'DMG': 50,
    'STA': 15,
    'Hold': 1,
    'Priority': 2,
}
STONE_WALL_DATA = {
    'Name': 'Stone Wall',
    'Type': Types.earth,
    'Synergy Type': None,
    'Class': 'Status',
    'DMG': 0,
    'STA': 18,
    'Hold': 1,
    'Priority': 1,
}

# for temtem.py
GYALIS_IMPORT = '''Gyalis @ Ice Cube
Trait: Resistant
TVs: 350 HP / 4 Sta / 146 Spe / 498 Atk / 1 Def / 1 SpD
SVs: 0 SpA
- Heat Up
- Crystal Bite
- Haito Uchi
- Sharp Stabs
'''
KINU_IMPORT = ''' Kinu @ Grease
Trait: Protector
TVs: 500 HP / 455 Def / 45 SpA
- Beta Burst
- Revitalize
- Stone Wall
- Turbo Choreography
'''
MULTI_IMPORT = f'{GYALIS_IMPORT}\n{KINU_IMPORT}'
GYALIS_STATS = {
    Stats.HP: 222,
    Stats.Sta: 52,
    Stats.Spe: 129,
    Stats.Atk: 151,
    Stats.Def: 83,
    Stats.SpA: 26,
    Stats.SpD: 83,
}

from temtem import TemTem
GYALIS_TEM = TemTem(
    'Gyalis',
    ['Heat Up', 'Crystal Bite', 'Haito Uchi', 'Sharp Stabs'],
    'Resistant',
    svs={'SpA': 0},
    tvs={'HP': 350, 'Sta': 4, 'Spe': 146, 'Atk': 498, 'Def': 1, 'SpD': 1},
    item='Ice Cube',
)
KINU_TEM = TemTem(
    'Kinu',
    ['Beta Burst', 'Revitalize', 'Stone Wall', 'Turbo Choreography'],
    'Protector',
    tvs={'HP': 500, 'Def': 455, 'SpA': 45},
    item='Grease',
)
