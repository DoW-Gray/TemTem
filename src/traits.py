# vim: set fileencoding=utf-8 :
"""
traits.py: All instances of the Trait class
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
from .effects import (
    Effect,
    Trait,
    no_effect,
    string_to_class_name,
    Unaffected,
    RedirectAttack
)

import logging
log = logging.getLogger(__name__)

_ALL_TRAITS = {}


def trait(cls):
    global _ALL_TRAITS
    _ALL_TRAITS[cls.__name__] = cls
    return cls


def lookup_trait(name, /):
    class_name = string_to_class_name(name)
    if class_name == '':
        return NoTrait
    try:
        return _ALL_TRAITS[class_name]
    except KeyError:
        log.error('Unable to find trait %s.', name)
        return NoTrait


class NoTrait(Trait):
    pass


@trait
class Aerobic(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        # trait counter ensures no double-boost for multi-target moves
        if attack['type'] == Types.wind and not attacker.trait_counter:
            return Effect(attacker={Stats.Spe: 1, Stats.SpD: -1, 'trait counter': 1})
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter:
            return Effect(target={'trait counter': 0})
        return no_effect


@trait
class AirSpecialist(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.wind:
            return Effect(damage=1.15)
        return no_effect


@trait
class Amphibian(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.water:
            return Effect(target={Stats.Spe: 1})
        return no_effect


@trait
class Anaerobic(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.toxic:
            return Effect(target={Stats.SpA: -1, Stats.SpD: 1})
        return no_effect


@trait
class Apothecary(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] != 'Special':
            return no_effect
        if target is attacker.ally:
            return Effect(target={Statuses.regenerated: 1})
        return Effect(target={Statuses.poisoned: 1})


@trait
class Autotomy(Trait):
    @staticmethod
    def on_switch_in(target):
        if target.trait_counter:
            return no_effect
        return Effect(target={Statuses.evading: 2, 'trait counter': 1})


@trait
class Avenger(Trait):
    @staticmethod
    def on_ally_damage(attacker, target, ally, attack, damage):
        if damage > target.live_stats[Stats.HP]:
            return Effect(ally={Stats.Spe: 1, Stats.SpA: 1})
        return no_effect


@trait
class Benefactor(Trait):
    @staticmethod
    def on_ally_damage(attacker, target, ally, attack, damage):
        return Effect(ally={Stats.HP: 0.1})


@trait
class BodyStretch(Trait):
    @staticmethod
    def on_rest(target):
        return Effect(target={Statuses.regenerated: 2})


@trait
class BookLungs(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.water:
            return Effect(damage=0.7)
        return no_effect


@trait
class Botanist(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.nature:
            return Effect(damage=1.15)
        return no_effect


@trait
class Botanophobia(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.nature:
            return Effect(damage=1.5)
        return no_effect


@trait
class Brawny(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] == 'Physical':
            return Effect(damage=1.2)
        return no_effect


@trait
class Bully(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        raise NotImplementedError()


@trait
class Burglar(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if target.asleep or target.exhausted:
            return Effect(target={'remove gear': True})
        return no_effect


@trait
class Caffeinated(Trait):
    @staticmethod
    def on_status(target, status, count):
        return Effect(target={Statuses.asleep: -1})


@trait
class Callosity(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['class'] == 'Physical':
            return Effect(target={Stats.Def: 1})
        return no_effect


@trait
class Camaraderie(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        raise NotImplementedError()


@trait
class Channeler(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] == 'Special':
            return Effect(damage=1.25)
        return no_effect


@trait
class Cobweb(Trait):
    @staticmethod
    def after_attack(attacker, target, attack):
        if target.poisoned:
            return Effect(target={Statuses.trapped: 2})
        return no_effect


@trait
class Confined(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if (
            (attacker is target and Statuses.trapped in attack['effects'])
            or Statuses.trapped in attack['self']
        ):
            return Effect(attacker={Stats.Def: 1, Stats.SpD: 1})
        return no_effect


@trait
class ColdNatured(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status == Statuses.cold:
            return Effect(target={Statuses.Cold: -1, Statuses.Frozen: count})
        return no_effect


@trait
class CowardsRest(Trait):
    @staticmethod
    def on_rest(target):
        return Effect(target={Statuses.evading: 2})

# TODO: deceit aura


@trait
class Demoralize(Trait):
    @staticmethod
    def on_switch_in(target):
        return Effect(opposing_team={Stats.Spe: -1})


@trait
class Determined(Trait):
    # handled in temtem.TemTem.apply_boost()
    pass


# TODO: dreaded alarm


@trait
class Earthbound(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        # trait counter ensures no double-boost for multi-target moves
        if attack['type'] == Types.earth and not attacker.trait_counter:
            return Effect(attacker={Stats.Def: 1, 'trait counter': 1})
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter:
            return Effect(attacker={'trait counter': 0})
        return no_effect

# TODO: efficient


@trait
class ElectricSynthesize(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.electric:
            return Effect(damage=-1)
        return no_effect


@trait
class EnergyReserves(Trait):
    @staticmethod
    def on_turn_end(target):
        if target.live_stats[Stats.HP] < target.stats[Stats.HP] / 4:
            return Effect(target={Statuses.vigorized: 2})
        return no_effect


@trait
class Escapist(Trait):
    @staticmethod
    def on_switch_in(target):
        if target.ally.trapped:
            return Effect(ally={Statuses.trapped: -1})
        return no_effect

    @staticmethod
    def on_status(target, status, count):
        if status == Statuses.trapped:
            return Effect(target={Statuses.trapped: -1})
        return no_effect

    @staticmethod
    def on_ally_status(target, ally, status, count):
        if status == Statuses.trapped:
            return Effect(target={Statuses.trapped: -1})
        return no_effect


@trait
class FaintedCurse(Trait):
    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        if damage <= target.live_stats[Stats.HP]:
            return no_effect
        return Effect(attacker={Statuses.HP: -int(attacker.stats[Stats.HP] * 0.3)})


@trait
class FastCharge(Trait):
    @staticmethod
    def on_ally_switch_in(target, ally):
        if Types.digital in ally.types:
            return Effect(ally={Stats.Spe: 2})
        return no_effect


@trait
class FeverRush(Trait):
    @staticmethod
    def on_status(target, status, count):
        return Effect(target={Stats.Atk: 1})


@trait
class FlawedCrystal(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] in {Types.mental, Types.toxic, Types.electric}:
            return Effect(damage=1.5)
        return no_effect


@trait
class Friendship(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attacker is target.ally:
            raise Unaffected()
        return no_effect


@trait
class Furor(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attacker.live_stats[Stats.HP] < attacker.stats[Stats.HP] * 0.33:
            return Effect(damage=1.33)
        return no_effect


@trait
class Guardian(Trait):
    @staticmethod
    def on_ally_status(target, ally, status, count):
        # Note: this also stops Frozen on a cold-natured ally (tested in-game)
        if status in {
            Statuses.cold,
            Statuses.frozen,
            Statuses.burned,
            Statuses.poisoned,
            Statuses.doomed
        }:
            return Effect(target={status: -1})
        return no_effect


@trait
class HeatDischarge(Trait):
    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        if damage > target.live_stats[Stats.HP]:
            return Effect(attacker={Statuses.burned: 3})
        return no_effect


@trait
class Hover(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.earth:
            return Effect(damage=0.5)
        return no_effect

# TODO: hurrywart, and hold as a whole


@trait
class Hydrologist(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.water:
            return Effect(damage=1.15)
        return no_effect


@trait
class Immunity(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.toxic:
            return Effect(damage=0)
        return no_effect


@trait
class Individualist(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if target is attacker.ally:
            raise Unaffected()
        return no_effect

# TODO: inductor, last rush, loneliness, marathonist


@trait
class MentalAlliance(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attacker.ally and Types.mental in attacker.ally.types:
            return Effect(damage=1.15)
        return no_effect


@trait
class Mirroring(Trait):
    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        if attack['class'] == 'Special':
            return Effect(attacker={Stats.HP: -damage // 4})
        return no_effect


@trait
class Mithridatism(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status == Statuses.poisoned:
            return Effect(target={Statuses.poisoned: -1})
        return no_effect

# TODO: motivator


@trait
class Mucous(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.electric:
            return Effect(damage=0.7)
        return no_effect

    @staticmethod
    def on_status(target, status, count):
        if status in {Statuses.cold, Statuses.burned}:
            return Effect(target={status: -1})
        return no_effect


@trait
class Neutrality(Trait):
    @staticmethod
    def on_status(target, status, count):
        return Effect(target={status: -1})


@trait
class Parrier(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['class'] == 'Physical':
            return Effect(damage=0.7)
        return no_effect


@trait
class Patient(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        # trait counter ensures no double-boost for multi-target moves
        if attack['hold'] and not attacker.trait_counter:
            return Effect(
                attacker={
                    Stats.Sta: attacker.stats[Stats.Sta] // 10,
                    'trait counter': 1
                }
            )
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter:
            return Effect(target={'trait counter': 0})
        return no_effect

# TODO: plethoric


@trait
class PowerNap(Trait):
    @staticmethod
    def on_turn_start(target):
        if target.asleep:
            return Effect(target={Stats.HP: int(target.stats[Stats.HP] * 1.15)})
        return no_effect


@trait
class Prideful(Trait):
    @staticmethod
    def after_attack(attacker, target, attack):
        if target.live_stats[Stats.HP] <= 0:
            return Effect(attacker={Stats.Atk: 1, Stats.SpA: 1, Stats.Spe: 1})
        return no_effect


@trait
class Protector(Trait):
    @staticmethod
    def on_switch_in(target):
        return Effect(ally={Stats.Def: 1, Stats.SpD: 1})


@trait
class Provident(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['class'] == 'Physical' and attack['type'] in {
            Types.fire, Types.earth, Types.melee
        }:
            return Effect(target={Stats.SpD: 1})
        return no_effect


@trait
class PunchingBag(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.melee:
            return Effect(damage=0.7)
        return no_effect


@trait
class PuppetMaster(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if (
            target.live_stats[Stats.HP] < target.stats[Stats.HP] * 0.4
            and target.ally
        ):
            raise RedirectAttack('ally')
        return no_effect


@trait
class Pyromaniac(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.fire:
            return Effect(damage=1.15)
        return no_effect


@trait
class Receptive(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status in {
            Statuses.vigorized,
            Statuses.immune,
            Statuses.regenerated,
            Statuses.evading,
            Statuses.alerted,
        }:
            return Effect(target={status: count + 1})
        return no_effect


@trait
class Rejuvenate(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] != 'Physical':
            return no_effect
        return Effect(attacker={Stats.HP: int(attacker.stats[Stats.HP] * 0.15)})


@trait
class Resiliant(Trait):
    # this is handled in TemTem.use_stamina
    pass


@trait
class Resistant(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status in {
            Statuses.cold,
            Statuses.asleep,
            Statuses.trapped,
            Statuses.poisoned,
            Statuses.burned,
            Statuses.exhausted,
        }:
            return Effect(target={status: count - 1 or -1})
        return no_effect


@trait
class Rested(Trait):
    # TODO: test if this is per battle, or per switchin
    # If per switchin, I'll need to add an on_switch_in to reset
    # TODO: ensure I'm not reading this wrong and it's a 1x mod turn 1, 1.3x t2,
    # 1.6x t3 onwards.
    @staticmethod
    def on_attack(attacker, target, attack):
        if attacker.trait_counter <= 2:
            return Effect(damage=1.3)
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter <= 2:
            return Effect(target={'trait counter': target.trait_counter + 1})
        return no_effect


# TODO: scavenger


@trait
class SelfEsteem(Trait):
    @staticmethod
    def after_attack(attacker, target, attack):
        if target.live_stats[Stats.HP] <= 0:
            return Effect(
                attacker={
                    Statuses.cold: -1,
                    Statuses.trapped: -1,
                    Statuses.seized: -1,
                    Statuses.poisoned: -1,
                    Statuses.burned: -1,
                    Statuses.doomed: -1,
                    Statuses.isolated: -1,
                    Statuses.exhausted: -1,
                },
            )
        return no_effect


# TODO: sensei


@trait
class Settling(Trait):
    @staticmethod
    def on_switch_in(target):
        return Effect(target={'trait counter': 0})

    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] == 'Physical':
            # TODO: check this isn't compound
            return Effect(damage=1 + 0.08 * attacker.trait_counter)
        return no_effect

    @staticmethod
    def on_turn_end(target):
        return Effect(target={'trait counter': target.trait_counter + 1})


@trait
class SharedPain(Trait):
    @staticmethod
    def on_turn_start(target):
        return Effect(target={'trait counter': 0})

    @staticmethod
    def on_hit(attacker, target, attack):
        if target.trait_counter and target.ally:
            raise RedirectAttack('ally')
        return Effect(target={'trait counter': 1})


@trait
class SkullHelmet(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] in {Types.melee, Types.mental}:
            return Effect(damage=0.75)
        return no_effect

# TODO: soft touch


@trait
class Spoilsport(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['target'] in {'team or ally', 'whole team', 'all'}:
            # TODO: check clockwise not included. Is that even testable?
            return Effect(damage=1.25)
        return no_effect

# TODO: spreader


@trait
class StrongLiver(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.toxic:
            return Effect(damage=-1)
        return no_effect


@trait
class SynergyMaster(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['synergy move']:
            return Effect(damage=1.25)
        return no_effect

    @staticmethod
    def on_ally_attack(attacker, target, attack):
        if attack['synergy move']:
            return Effect(damage=1.25)
        return no_effect


@trait
class TacticalStrike(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['hold']:
            return Effect(damage=1.15)
        return no_effect


@trait
class TardyRush(Trait):
    # TODO: speed up after 3 turns
    @staticmethod
    def on_switch_in(target):
        return Effect(target={'trait counter': 0})

    @staticmethod
    def on_attack(attacker, target, attack):
        if attacker.trait_counter >= 3 and attack['trait'] == 'Physical':
            return Effect(damage=1.1)
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter < 3:
            return Effect(target={'trait counter': target.trait_counter + 1})
        return no_effect


@trait
class TeamElusive(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['target'] in {'team or ally', 'whole team', 'all'}:
            raise Unaffected()
        return no_effect


@trait
class ThickSkin(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['type'] == Types.wind:
            return Effect(damage=0.5)
        return no_effect


@trait
class Tireless(Trait):
    # this is handled in TemTem.use_stamina
    pass


@trait
class ToxicAffinity(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.toxic:
            return Effect(damage=1.5)
        return no_effect


@trait
class ToxicFarewell(Trait):
    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        if damage >= target.live_stats[Stats.HP]:
            return Effect(attacker={Statuses.poisoned: 3})
        return no_effect


@trait
class ToxicSkin(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['class'] == 'Physical':
            return Effect(attacker={Statuses.poisoned: 2})
        return no_effect


@trait
class Trance(Trait):
    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        res_hp = target.live_stats[Stats.HP] - damage
        if res_hp <= 0 or res_hp > target.stats[Stats.HP] * 0.3:
            return no_effect
        return Effect(
            target={
                Statuses.asleep: 2,
                Statuses.regenerated: 2,
                Stats.SpA: 2,
                Stats.SpD: 2,
            }
        )


@trait
class Trauma(Trait):
    @staticmethod
    def on_hit(attacker, target, attack):
        if attack['class'] == 'Physical':
            return Effect(target={Stats.Def: -1})
        elif attack['class'] == 'Special':
            return Effect(target={Stats.SpD: -1})
        return no_effect


@trait
class TriApothecary(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['class'] != 'Special':
            return no_effect
        if target is attacker.ally:
            return Effect(target={Statuses.regenerated: 3})
        return Effect(target={Statuses.poisoned: 3})


@trait
class Unnoticed(Trait):
    @staticmethod
    def on_turn_start(target):
        return Effect(target={'trait counter': 0})

    @staticmethod
    def on_switch_in(target):
        return Effect(target={'trait counter': 0})

    @staticmethod
    def on_hit(attacker, target, attack):
        if target.trait_counter:
            return no_effect
        return Effect(target={'trait counter': 1})

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter:
            return no_effect
        return Effect(target={Stats.Spe: 1})


@trait
class Vigorous(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attacker.trait_counter == 1:
            # This is set in TemTem.use_stamina(). Simply checking if
            # overexerted would cause strangle to increase attack power.
            return Effect(damage=1.5, attacker={'trait counter': 0})
        return no_effect

    @staticmethod
    def on_turn_end(target):
        if target.trait_counter:
            return Effect(target={'trait counter': 0})
        return no_effect


@trait
class WarmBlooded(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status == Statuses.cold:
            return Effect(target={Statuses.cold: -1})
        return no_effect


@trait
class WaterAffinity(Trait):
    @staticmethod
    def on_attack(attacker, target, attack):
        if attack['type'] == Types.water:
            return Effect(damage=1.5)
        return no_effect


@trait
class WaterCustodian(Trait):
    @staticmethod
    def on_ally_hit(attacker, target, attack):
        if attack['type'] == Types.water:
            raise RedirectAttack('ally')
        return no_effect


@trait
class Withdrawal(Trait):
    @staticmethod
    def on_rest(target):
        if target.asleep:
            raise NotImplementedError()
            # TODO: work out what happens with sleep - does the tem get alerted
            # instead?
        return Effect(target={Stats.HP: int(target.stats[Stats.HP] * 0.15)})


@trait
class WreckedFarewell(Trait):
    @staticmethod
    def on_take_damage(attacker, target, ally, attack, damage):
        if damage >= target.live_stats[Stats.HP] and (
            attacker is None or attacker is target
        ):
            return Effect(ally={Stats.HP: -0.25}, opposing_team={Stats.HP: -0.25})


@trait
class Zen(Trait):
    @staticmethod
    def on_status(target, status, count):
        if status == Statuses.asleep:
            return Effect(target={Stats.Def: 1, Stats.SpD: 1})
        return no_effect
