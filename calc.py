# vim: set fileencoding=utf-8 :
"""
calc.py: various damage calculation functions
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

from static import (
    Stats,
    TYPE_EFFECTIVENESS,
    lookup_attack,
)

def calc_damage(attacker, attack, target):
    if isinstance(attack, str):
        attack = lookup_attack(attack)

    damage = attacker.level * attack['DMG']
    if cl := attack['Class'] == 'Status':
        return 0
    elif cl == 'Physical':
        damage *= attacker.live_stats[Stats.Atk] / target.live_stats[Stats.Def]
    else:
        damage *= attacker.live_stats[Stats.Atk] / target.live_stats[Stats.Def]
    damage /= 200
    damage += 7
    damage *= effectiveness(attack['Type'], target)
    if attack['Type'] in attacker.types:
        damage *= 1.5  # STAB

    return max(1, int(damage))

def effectiveness(attack_type, target):
    return (
        TYPE_EFFECTIVENESS[attack_type][target.types[0]]
        * (
            TYPE_EFFECTIVENESS[attack_type][target.types[1]]
            if target.types[1] else 1.0
        )
    )

def n_hko(attacker, attack, target):
    damage = calc_damage(attacker, attack, target)
    return target.stats[Stats.HP] // damage + 1


### Tests
def test_effectiveness():
    from test_data import GYALIS_TEM, KINU_TEM
    from static import Types

    assert effectiveness(Types.fire, GYALIS_TEM) == 2.0
    assert effectiveness(Types.crystal, GYALIS_TEM) == 1.0
    assert effectiveness(Types.electric, GYALIS_TEM) == 0.5

    prev_types = KINU_TEM.types
    KINU_TEM.types = (Types.nature, Types.crystal)
    assert effectiveness(Types.fire, KINU_TEM) == 4.0
    KINU_TEM.types = prev_types

def test_calc_damage():
    from test_data import GYALIS_TEM, KINU_TEM

    assert calc_damage(KINU_TEM, 'Turbo Choreography', GYALIS_TEM) == 0
    # TODO: confirm the below values
    assert calc_damage(KINU_TEM, 'Beta Burst', GYALIS_TEM) == 43
    assert calc_damage(GYALIS_TEM, 'Crystal Bite', KINU_TEM) == 149
    assert calc_damage(GYALIS_TEM, 'Haito Uchi', KINU_TEM) == 26
