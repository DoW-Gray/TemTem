# vim: set fileencoding=utf-8 :
"""
effects.py: Class for effects, like those from traits
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

from static import Statuses, Stats


class DontApplyStatus(Exception):
    pass


class RedirectAttack(Exception):
    def __init__(self, new_target, *args, **kwargs):
        self.new_target = new_target
        super().__init__(*args, **kwargs)


class Unaffected(Exception):
    pass


class Effect:
    def __init__(
        self,
        *,
        attacker={},
        target={},
        ally={},
        opposing_team={},
        damage=1,
    ):
        self.attacker = attacker
        self.target = target
        self.ally = ally
        self.opposing_team = opposing_team
        self.damage = damage

    def __repr__(self):
        res = ''
        for name, var in (
            ('attacker', self.attacker),
            ('target', self.target),
            ('ally', self.ally),
            ('opposing team', self.opposing_team)
        ):
            if var:
                res += f' {name}: {str(var)}'
        if self.damage != 1:
            res += f' damage: {self.damage}'
        return f'<Effect{res}>'

    def apply(
        self,
        attacker=None,
        target=None,
        ally=None,
        opposing_team=None,
        damage=1,
    ):
        from contextlib import suppress

        def apply_effect(tem, effect, count):
            from gear import NoGear
            if effect in Stats:
                tem.apply_boost(effect, count)

            elif effect in Statuses:
                if count < 1:  # remove this status
                    with suppress(KeyError):
                        del tem.statuses[effect]
                        if effect == Statuses.asleep:
                            tem.apply_status(Statuses.alerted, 2)
                            # The above doesn't trigger if tem wasn't asleep
                            # due to the KeyError
                    raise DontApplyStatus()
                else:
                    if effect in (Stats.HP, Stats.Sta):
                        raise NotImplementedError()
                    tem.apply_status(effect, count)

            else:
                # Unusual effects, handling e.g. strangle
                if effect == 'trait counter':
                    tem.trait_counter = count
                elif effect == 'remove gear':
                    tem.gear = NoGear
                elif effect == 'overexerted':
                    tem.overexerted = 2  # equal to "used up all its stamina this turn"
                elif effect == 'clear boosts':
                    tem.boosts = {
                        stat: 0
                        for stat in Stats
                        if stat not in (Stats.HP, Stats.Sta)
                    }
                    tem._calc_live_stats()
                else:
                    raise NotImplementedError()

        no_status = False
        for effects, tem in (
            (self.attacker, attacker),
            (self.target, target),
            (self.ally, ally),
        ):
            for effect, count in effects.items():
                try:
                    apply_effect(tem, effect, count)
                except DontApplyStatus:
                    no_status = True

        if self.opposing_team:
            for tem in opposing_team:
                for effect, count in effects.items():
                    apply_effect(tem, effect, count)

        if no_status:
            raise DontApplyStatus()

        return damage * self.damage

    def prevents_status(self, status):
        try:
            return self.target[status] < 1
        except KeyError:
            return False


no_effect = Effect()


class EffectHandler:
    # callback functions
    @staticmethod
    def on_switch_in(target):
        return no_effect

    @staticmethod
    def on_ally_switch_in(target, ally):
        return no_effect

    @staticmethod
    def on_turn_start(target):
        return no_effect

    @staticmethod
    def on_attack(attacker, target, attack):
        return no_effect

    @staticmethod
    def on_hit(attacker, target, attack):
        return no_effect

    @staticmethod
    def on_ally_attack(attacker, target, attack):
        return no_effect

    @staticmethod
    def on_ally_hit(attacker, target, attack):
        return no_effect

    @staticmethod
    def on_take_damage(attacker, target, attack, damage):
        return no_effect

    @staticmethod
    def on_ally_damage(attacker, target, ally, attack, damage):
        return no_effect

    @staticmethod
    def on_status(target, status, count):
        return no_effect

    @staticmethod
    def on_ally_status(target, ally, status, count):
        return no_effect

    @staticmethod
    def on_rest(target):
        return no_effect

    @staticmethod
    def on_turn_end(target):
        return no_effect


class Trait(EffectHandler):
    # Defined for both readability and isinstance()
    pass


class Gear(EffectHandler):
    # Defined for both readability and isinstance()
    pass


def string_to_class_name(inpt):
    # Used in both gear.py and traits.py, so I put it here
    if inpt is None:
        return ''
    inpt = inpt.strip()
    if not inpt:
        return ''
    return inpt.replace(' ', '').replace('-', '').replace("'", '')
