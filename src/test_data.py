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
from .static import Stats, Types, Statuses
from .temtem import TemTem

GYALIS_DATA = {
    'Stats': {
        'BST': 460,
        Stats.HP: 86,
        Stats.Sta: 44,
        Stats.Spe: 100,
        Stats.Atk: 85,
        Stats.Def: 61,
        Stats.SpA: 23,
        Stats.SpD: 61,
    },
    'Types': (Types.crystal, Types.melee),
    'Traits': ('Mirroring', 'Resistant'),
    'Moves': {
        'Egg': ['Crystal Spikes', 'Crystallize', 'Earth Wave'],
        'Level Up': [
            'Kick',
            'Glass Blade',
            'Sharp Stabs',
            'Footwork',
            'Double Gash',
            'Block',
            'Drill Impact',
            'Crystal Bite',
            'Ninja Jutsu',
            'Hook Kick',
        ],
        'TC': ['Awful Song', 'Antitoxins', 'Rend', 'Footwork'],
    },
}
PIGEPIC_DATA = {
    'Stats': {
        'BST': 433,
        Stats.HP: 54,
        Stats.Sta: 72,
        Stats.Spe: 58,
        Stats.Atk: 60,
        Stats.Def: 72,
        Stats.SpA: 45,
        Stats.SpD: 72,
    },
    'Types': (Types.wind, None),
    'Traits': ('Friendship', 'Fainted Curse'),
    'Moves': {
        'Egg': ['Head Charge', 'Sharp Rain'],
        'Level Up': [
            'Bamboozle',
            'Scratch',
            'Nibble',
            'Nimble',
            'Heavy Blow',
            'Wind Burst',
            'Tornado',
            'Oshi-Dashi',
        ],
        'TC': [
            'Stone Wall',
            'Turbo Choreography',
            'Wake Up',
            'Misogi',
            'Confiscate',
            'Relax',
            'Major Slash'
        ],
    },
}
BETA_BURST_DATA = {
    'name': 'Beta Burst',
    'type': Types.mental,
    'class': 'Special',
    'damage': 100,
    'stamina': 23,
    'hold': 0,
    'priority': 2,
    'target': 'other',
}
HIGHPRESSURE_WATER_DATA = {
    'name': 'High-pressure Water',
    'type': Types.water,
    'synergy type': Types.fire,
    'class': 'Special',
    'damage': 50,
    'stamina': 15,
    'hold': 1,
    'priority': 2,
    'target': 'other',
}
HIGHPRESS_WATER_DATA_FIRE = {
    'name': 'High-pressure Water +Fire',
    'type': Types.water,
    'class': 'Special',
    'damage': 50,
    'stamina': 15,
    'hold': 1,
    'priority': 2,
    'target': 'other',
    'effects': {
        Statuses.burned: 3,
    },
}
STONE_WALL_DATA = {
    'name': 'Stone Wall',
    'type': Types.earth,
    'class': 'Status',
    'damage': 0,
    'stamina': 18,
    'hold': 1,
    'priority': 1,
    'target': 'single',
}
STARE_DATA = {
    'name': 'Stare',
    'type': Types.mental,
    'class': 'Status',
    'damage': 0,
    'stamina': 6,
    'hold': 0,
    'priority': 2,
    'target': 'other',
}

# for temtem.py
GYALIS_IMPORT = '''Gyalis @ IceCube
Trait: Resistant
Level: 48
TVs: 350 HP / 4 Sta / 146 Spe / 498 Atk / 1 Def / 1 SpD
SVs: 1 SpA
- Heat Up
- Crystal Bite
- Haito Uchi
- Sharp Stabs
'''
KINU_IMPORT = ''' Kinu @ Grease
Trait: Protector
Level: 48
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
    Stats.SpA: 27,
    Stats.SpD: 83,
}

GYALIS_TEM = TemTem(
    'Gyalis',
    ['Heat Up', 'Crystal Bite', 'Haito Uchi', 'Sharp Stabs'],
    'Resistant',
    svs={'SpA': 1},
    tvs={'HP': 350, 'Sta': 4, 'Spe': 146, 'Atk': 498, 'Def': 1, 'SpD': 1},
    gear='Ice Cube',
    level=48,
)
KINU_TEM = TemTem(
    'Kinu',
    ['Beta Burst', 'Revitalize', 'Stone Wall', 'Turbo Choreography'],
    'Protector',
    tvs={'HP': 500, 'Def': 455, 'SpA': 45},
    gear='Grease',
    level=48,
)
VOLAREND_TEM = TemTem(
    'Volarend',
    ['Wind Blade', 'Hyperkinetic Strike', 'Blizzard', 'Toxic Plume'],
    'Aerobic',
    tvs={'HP': 408, 'Sta': 90, 'Spe': 500, 'Def': 1, 'SpA': 1},
    gear='Hand Fan',
    level=48,
)
