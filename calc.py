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
    Types,
    Statuses,
    TYPE_EFFECTIVENESS,
    ITEM_DAMAGE_TYPES,
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
    if attack['name'] == 'Hyperkinetic Strike':
        damage += 64 * attacker.live_stats[Stats.Spe] / target.live_stats[Stats.SpD]

    damage *= attacker.level

    if Statuses.burned in attacker.statuses:
        damage *= 0.7

    damage /= 200
    damage += 7
    damage *= effectiveness(attack['type'], target)

    if attack['type'] in attacker.types:
        damage *= 1.5  # STAB

    damage *= modifiers

    if abs(damage) < 1 and damage != 0.0:
        # Damage should always be at least 1, unless target is immune
        return -1 if damage < 0 else 1
    return int(damage)


def effectiveness(attack_type, target):
    if Statuses.nullified in target.statuses:
        return 1.0

    return (
        TYPE_EFFECTIVENESS[attack_type][target.types[0]]
        * (
            TYPE_EFFECTIVENESS[attack_type][target.types[1]]
            if target.types[1] else 1.0
        )
    )


def trait_modifiers(attacker, attack, target):
    res = 1.0

    # Type-specific traits
    if attack['type'] == Types.wind:
        if attacker.trait == 'Air Specialist':
            res *= 1.15
    elif attack['type'] == Types.nature:
        if attacker.trait == 'Botanist':
            res *= 1.15
        if target.trait == 'Botanophobia':
            res *= 1.5
    elif attack['type'] == Types.fire:
        if attacker.trait == 'Pyromaniac':
            res *= 1.15
        if target.trait == 'Thick Skin':
            res *= 0.5
    elif attack['type'] == Types.water:
        if attacker.trait == 'Hydrologist':
            res *= 1.15
        elif attacker.trait == 'Water Affinity':
            # I'm assuming this stacks with STAB, like Toxic Affinity
            res *= 1.5
    elif attack['type'] == Types.electric:
        if target.trait == 'Mucous':
            res *= 0.7
        elif target.trait == 'Flawed Crystal':
            res *= 1.5
        elif target.trait == 'Electric Synthesize':
            res *= -1
    elif attack['type'] == Types.toxic:
        if attacker.trait == 'Toxic Affinity':
            res *= 1.5
        if target.trait == 'Immunity':
            return 0.0
        elif target.trait == 'Flawed Crystal':
            res *= 1.5
    elif attack['type'] == Types.mental:
        if target.trait == 'Flawed Crystal':
            res *= 1.5
        elif target.trait == 'Strong Liver':
            res *= -1
    elif attack['type'] == Types.earth:
        if target.trait == 'Hover':
            res *= 0.5
    elif attack['type'] == Types.melee:
        if target.trait == 'Punching Bag':
            res *= 0.7

    # Other traits
    # TODO: handle Settling, Rested, Shared Pain, Puppet Master,
    # Camaraderie, Bully, Last Rush
    if attack['class'] == 'Physical':
        if attacker.trait == 'Brawny':
            res *= 1.2
        if target.trait == 'Parrier':
            res *= 0.7
        elif target.trait == 'Punching Bag':
            res *= 1.3
    elif attack['class'] == 'Special':
        if attacker.trait == 'Channeler':
            res *= 1.25
        elif attacker.trait == 'Mental Alliance':
            if attacker.ally and Types.mental in attacker.ally.types:
                res *= 1.15

    if attacker.ally is None:
        # TODO: check Last Rush here
        pass
    else:
        if target is attacker.ally:
            if attacker.trait == 'Individualist':
                return 0.0
            elif target.trait == 'Friendship':
                return 0.0
        if target.trait == 'Synergy Master' and 'synergy move' in attack:
            res *= 1.25

    if (
        attack['target'] in {'clockwise', 'team or ally', 'whole team', 'all'}
        and attacker.trait == 'Spoilsport'
    ):
        res *= 1.25

    elif attacker.trait == 'Vigorous' and attacker.overexerted:
        res *= 1.5

    elif (
        attacker.trait == 'Furor'
        and attacker.live_stats[Stats.HP] < attacker.stats[Stats.HP] / 3
    ):
        res *= 1.33  # TODO: check if this should be + 1/3

    return res


def item_modifiers(attacker, attack, target):
    from contextlib import suppress
    res = 1.0
    with suppress(KeyError):
        atk_item, def_item = ITEM_DAMAGE_TYPES[attack['type']]
        if (
            (attacker.item == atk_item and Statuses.seized not in attacker.statuses)
            and (target.item != 'Snare' and Statuses.seized not in target.statuses)
        ):
            res *= 1.1
        if target.item == def_item and Statuses.seized not in target.statuses:
            res *= 0.8
    return res


def n_hko(attacker, attack, target):
    damage = calc_damage(attacker, attack, target)
    return target.stats[Stats.HP] // damage + 1


# Tests
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
    from test_data import GYALIS_TEM, KINU_TEM, VOLAREND_TEM

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

    # Hyperkinetic Strike weirdness
    # Note: this calculation disagrees with TesTem. At the time TesTem 0.5.1 was
    # released, the wiki stated 59 * Spe / SpD (rather than 64); this info is
    # out of date. So I'm confident my answer is correct, even though I haven't
    # double-checked in-game.
    assert calc_damage(VOLAREND_TEM, 'Hyperkinetic Strike', KINU_TEM) == 56
    # Note: the above does not include the Hand Fan modifier.
