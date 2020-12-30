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
    Statuses,
    Types,
    TYPE_EFFECTIVENESS,
    lookup_attack,
)
from .temtem import TemTem

from typing import Any


def calc_damage(
    attacker: TemTem, target: TemTem, attack: Any,  modifiers: float = 1.0
) -> int:
    """
    formula (from the wiki, alongside discussion with a few prominent folks):

    damage = (7 + (lvl / 200) * atk_dmg * (atk / def)) * modifiers
           = ((lvl * atk_dmg * atk) / (200 * def) + 7) * modifiers

    Note that a few modifiers e.g. burn affect the stats, rather than the
    damage - these are assumed to be applied already

    The result of this is rounded before being returned.
    """
    if isinstance(attack, str):
        attack = lookup_attack(attack)

    if (cls := attack['class']) == 'Status':
        return 0
    elif cls == 'Physical':
        atk = attacker.Atk
        df = target.Def
    else:
        atk = attacker.SpA
        df = target.SpD

    damage = (attacker.level * attack['damage'] * atk) / (200 * df) + 7
    damage *= effectiveness(attack['type'], target)
    damage *= modifiers

    stab = 1.5 if attack['type'] in attacker.types else 1.0

    if attack['name'] == 'Hyperkinetic Strike':
        # Currently modifiers above here in the code aren't included in the
        # game, but this is a bug. I'm informed the move should also use ceil
        # rather than floor, and 64 for the base damge of this part.
        damage += (attacker.level * 59 * attacker.Spe) / (200 * df)

        # I haven't found any documentation that hks works this way, but it
        # perfectly matches results I see, and is the simplest such answer.
        return int(damage * stab)

    return round(damage * stab)


def effectiveness(attack_type: Types, target: TemTem) -> float:
    if target.nullified:
        return 1.0

    return (
        TYPE_EFFECTIVENESS[attack_type][target.types[0]]
        * (
            TYPE_EFFECTIVENESS[attack_type][target.types[1]]
            if target.types[1] else 1.0
        )
    )


def n_hko(
    attacker: TemTem, target: TemTem, attack: Any, modifiers: float = 1.0
) -> int:
    from math import ceil, inf

    damage = calc_damage(attacker, target, attack, modifiers)
    if damage <= 0:
        return inf  # I think this makes more sense than DivisionByZeroError()
    return ceil(target.max_hp / damage)


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
    assert calc_damage(KINU_TEM, GYALIS_TEM, 'Turbo Choreography') == 0
    assert calc_damage(KINU_TEM, GYALIS_TEM, 'Beta Burst') == 51
    assert calc_damage(GYALIS_TEM, KINU_TEM, 'Crystal Bite') == 149
    assert calc_damage(GYALIS_TEM, KINU_TEM, 'Earth Wave') == 18

    # Check burn reduces damage correctly
    GYALIS_TEM.apply_status(Statuses.burned, 2)
    assert calc_damage(GYALIS_TEM, KINU_TEM, 'Crystal Bite') == 110
    GYALIS_TEM.statuses = {}
    KINU_TEM.apply_status(Statuses.burned, 2)
    assert calc_damage(KINU_TEM, GYALIS_TEM, 'Beta Burst') == 39
    KINU_TEM.statuses = {}

    # Very weird, currently buggy Hyperkinetic Strike. I've confirmed this value
    # is currently correct against the game, as well as the tem.team calc, but
    # I'm told the current behaviour is considered buggy, and may well change
    # in the near future (but to something simpler).
    assert calc_damage(VOLAREND_TEM, KINU_TEM, 'Hyperkinetic Strike') == 56
    # Note: the above does not include the Hand Fan modifier.
