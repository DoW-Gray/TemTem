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

from .static import (
    Stats,
    Statuses,
    TYPE_EFFECTIVENESS,
    lookup_attack,
)


def calc_damage(attacker, attack, target, modifiers=1.0):
    if isinstance(attack, str):
        attack = lookup_attack(attack)

    damage = attack['damage']
    if (cl := attack['class']) == 'Status':
        return 0
    elif cl == 'Physical':
        damage *= attacker.live_stats[Stats.Atk] / target.live_stats[Stats.Def]
    else:
        damage *= attacker.live_stats[Stats.SpA] / target.live_stats[Stats.SpD]

    damage *= attacker.level

    if attacker.burned:
        damage *= 0.7

    damage /= 200
    damage += 7
    damage *= effectiveness(attack['type'], target)

    damage *= modifiers

    if attack['name'] == 'Hyperkinetic Strike':
        # Currently modifiers above here in the code aren't included in the
        # game, but this is a bug. I'm informed the move should also use ceil
        # rather than floor, and 64 for the base damge of this part.
        damage += (
            (attacker.level / 200)
            * (attacker.live_stats[Stats.Spe] / target.live_stats[Stats.SpD])
            * 59
        )

    if attack['type'] in attacker.types:
        damage *= 1.5  # STAB

    if abs(damage) < 1 and damage != 0.0:
        # Damage should always be at least 1, unless target is immune
        return -1 if damage < 0 else 1
    return int(damage)


def effectiveness(attack_type, target):
    if target.nullified:
        return 1.0

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


# Tests
def test_effectiveness():
    from .test_data import GYALIS_TEM, KINU_TEM
    from .static import Types

    assert effectiveness(Types.fire, GYALIS_TEM) == 2.0
    assert effectiveness(Types.crystal, GYALIS_TEM) == 1.0
    assert effectiveness(Types.electric, GYALIS_TEM) == 0.5

    prev_types = KINU_TEM.types
    KINU_TEM.types = (Types.nature, Types.crystal)
    assert effectiveness(Types.fire, KINU_TEM) == 4.0
    KINU_TEM.types = prev_types


def test_calc_damage():
    from .test_data import GYALIS_TEM, KINU_TEM, VOLAREND_TEM

    # Regular moves
    assert calc_damage(KINU_TEM, 'Turbo Choreography', GYALIS_TEM) == 0
    assert calc_damage(KINU_TEM, 'Beta Burst', GYALIS_TEM) == 51
    assert calc_damage(GYALIS_TEM, 'Crystal Bite', KINU_TEM) == 149
    assert calc_damage(GYALIS_TEM, 'Earth Wave', KINU_TEM) == 18

    # Check burn reduces damage correctly
    GYALIS_TEM.apply_status(Statuses.burned, 2)
    assert calc_damage(GYALIS_TEM, 'Crystal Bite', KINU_TEM) == 110
    GYALIS_TEM.statuses = {}
    KINU_TEM.apply_status(Statuses.burned, 2)
    assert calc_damage(KINU_TEM, 'Beta Burst', GYALIS_TEM) == 39
    KINU_TEM.statuses = {}

    # Very weird, currently buggy Hyperkinetic Strike. I've confirmed this value
    # is currently correct against the game, as well as the tem.team calc, but
    # I'm told the current behaviour is considered buggy, and may well change
    # in the near future (but to something simpler).
    assert calc_damage(VOLAREND_TEM, 'Hyperkinetic Strike', KINU_TEM) == 56
    # Note: the above does not include the Hand Fan modifier.
