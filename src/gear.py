# vim: set fileencoding=utf-8 :
"""
gear.py: All instances of the Gear class
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

from .static import Statuses, Stats, Types
from .calc import effectiveness
from .effects import Effect, Gear, no_effect, string_to_class_name
from .temtem import TemTem

from typing import Type, Dict, Any

import logging
log = logging.getLogger(__name__)

_ALL_GEAR = {}


def gear(cls: Type[Gear]) -> Type[Gear]:
    global _ALL_GEAR
    _ALL_GEAR[cls.__name__] = cls
    return cls


def lookup_gear(name: str, /) -> Gear:
    class_name = string_to_class_name(name)
    if class_name == '':
        return NoGear
    try:
        return _ALL_GEAR[class_name]
    except KeyError:
        log.error('Unable to find gear %s', name)
        return NoGear


class NoGear(Gear):
    pass


@gear
class FireChip(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.fire:
            return Effect(damage=1.1)
        return no_effect


@gear
class HandFan(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.wind:
            return Effect(damage=1.1)
        return no_effect


@gear
class LightningRod(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.electric:
            return Effect(damage=0.8)
        return no_effect


@gear
class Pillow(Gear):
    @staticmethod
    def on_turn_start(target: TemTem) -> Effect:
        if target.asleep:
            return Effect(target={Stats.HP: target.max_hp // 10})
        return no_effect


@gear
class Pansunscreen(Gear):
    @staticmethod
    def on_status(target: TemTem, status: Statuses, count: int) -> Effect:
        if status == Statuses.burned:
            return Effect(target={Statuses.burned: -1})
        return no_effect


@gear
class Talisman(Gear):
    @staticmethod
    def on_status(target: TemTem, status: Statuses, count: int) -> Effect:
        if status == Statuses.doomed:
            return Effect(target={Statuses.doomed: -1})
        return no_effect


@gear
class Umbrella(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.water:
            return Effect(damage=0.8)
        return no_effect


@gear
class IceCube(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.fire:
            return Effect(damage=0.8)
        return no_effect


@gear
class EnergyDrink(Gear):
    @staticmethod
    def on_status(target: TemTem, status: Statuses, count: int) -> Effect:
        if status == Statuses.asleep:
            return Effect(target={Statuses.asleep: -1})
        return no_effect


@gear
class RockShield(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.crystal:
            return Effect(damage=0.8)
        return no_effect


@gear
class Sweatband(Gear):
    @staticmethod
    def on_turn_start(target: TemTem) -> Effect:
        return Effect(target={Stats.Sta: int(target.max_sta * 0.15)})


@gear
class TucmaMask(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.toxic:
            return Effect(damage=0.8)
        return no_effect


@gear
class Snare(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        return Effect(attacker={'remove gear': True}, target={'remove gear': True})


@gear
class Chamomile(Gear):
    @staticmethod
    def on_switch_in(target: TemTem) -> Effect:
        return Effect(target={'clear boosts': True, Statuses.immune: 4})


@gear
class Grease(Gear):
    @staticmethod
    def on_status(target: TemTem, status: Statuses, count: int) -> Effect:
        if status == Statuses.trapped:
            return Effect(target={Statuses.trapped: -1})
        return no_effect


@gear
class ShuinesHorn(Gear):
    # This is handled in TemTem.lookup_attack
    pass


@gear
class Coat(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.wind:
            return Effect(damage=0.8)
        return no_effect


@gear
class ResistanceBadge(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.neutral:
            return Effect(damage=1.15)
        return no_effect


@gear
class WarDrum(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['class'] == 'Physical':
            return Effect(damage=1.08)
        return no_effect

    @staticmethod
    def on_ally_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['class'] == 'Physical':
            return Effect(damage=1.08)
        return no_effect


@gear
class Turban(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.earth:
            return Effect(damage=0.8)
        return no_effect


@gear
class Handcuffs(Gear):
    @staticmethod
    def after_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if target.exhausted:
            return Effect(target={Statuses.trapped: 3})
        return no_effect


@gear
class Drill(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if target.evading:
            return Effect(target={Statuses.evading: -1})
        return no_effect

# TODO: strange vest


@gear
class BatonPass(Gear):
    @staticmethod
    def on_switch_in(target: TemTem) -> Effect:
        return Effect(target={Stats.HP: target.max_hp // 10})

# TODO: hopeless tonic


@gear
class DoubleScreen(Gear):
    @staticmethod
    def on_hit(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attacker.types[1] is not None:
            return Effect(damage=0.9)
        return no_effect


@gear
class IronCoating(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.earth:
            return Effect(damage=1.1)
        return no_effect


@gear
class Slingshot(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if effectiveness(attack['type'], target) == 0.25:
            return Effect(attacker={Stats.Def: 1, Stats.SpD: 1, Stats.Spe: 1})
        return no_effect

# TODO: doppelganger brooch


@gear
class SenseiRobe(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.melee and attack['class'] == 'Special':
            return Effect(damage=1.25)
        return no_effect


@gear
class AloeVera(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if target.types[0] == Types.toxic or target.types[1] == Types.toxic:
            return Effect(damage=1.15)
        return no_effect


@gear
class TinfoilHat(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.digital:
            return Effect(damage=0.7)
        return no_effect


@gear
class Taser(Gear):
    @staticmethod
    def on_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['type'] == Types.electric and attack['class'] == 'Special':
            return Effect(target={Statuses.burned: 1})
        return no_effect


@gear
class Matcha(Gear):
    @staticmethod
    def on_rest(target) -> Effect:
        return Effect(target={Statuses.cold: 0, Stats.Sta: target.max_sta * 0.4})


@gear
class ReactiveVial(Gear):
    @staticmethod
    def after_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if effectiveness(attack['type'], target) >= 1:
            return Effect(target={Stats.HP: target.max_hp * 0.15, Statuses.nullified: 1, 'remove gear': True})
        return no_effect


# TODO: implement target.after_attack in sim.py _process_attack for effects that happen to the defending TemTem after damage has been dealt.
# TODO: wiki says hacked microchip activates from offensive digital techniques, need to test whether status attacks that apply status effects such as burn will trigger this
@gear
class HackedMicrochip(Gear):
    @staticmethod
    def after_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if attack['class'] in {'self', 'team or ally', 'team', 'all'}:
            return no_effect
        if attack['class'] == 'Status':
            return no_effect
        return Effect(target={Statuses.evading: 2})


@gear
class FirstAidKit(Gear):
    @staticmethod
    def after_attack(attacker: TemTem, target: TemTem, attack: Dict[str, Any]) -> Effect:
        if target.stats[Stats.HP] < target.max_hp * 0.25:
            return Effect(target={Stats.HP: target.max_hp * 0.15, 'remove gear': True})
