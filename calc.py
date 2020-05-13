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

from consts import (
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
