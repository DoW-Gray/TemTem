# vim: set fileencoding=utf-8 :
"""
sim.py: code for simulating a temtem battle
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

from static import Stats, Types, Statuses, lookup_attack

from math import ceil, floor


class Choice:

    def __init__(self, action, detail=None, target=None):
        self.action = action
        self.detail = detail
        self.targets = target
        self.winner = None

    def priority(self, tem, attack_prio):
        speed = tem.live_stats[Stats.Spe]

        if self.action == 'run':
            return [4, speed]
        if self.action == 'item':
            return [3, speed]
        if self.action == 'switch':
            return [1, speed]
        if self.action == 'rest':
            return [-2, speed]

        # self.action must be 'attack', per choice_actions validation
        # self.detail at this point is an attack dict, per battle._lookup_attacks
        if attack_prio == 5:
            return [2, speed]
        if attack_prio == 0:
            return [-1, speed]

        priority_lookup = {
            1: 0.5,
            2: 1.0,
            3: 1.5,
            4: 1.75,
        }

        return [0, priority_lookup[attack_prio] * speed]


class Battle:

    def __init__(self, teams, active, speed_arrow):
        self.teams = teams
        self.active = active
        self.speed_arrow = speed_arrow  # 0 or 1
        self.winner = None

    def active_tem(self, side, slot):
        try:
            return self.teams[side][self.active[side][slot]]
        except KeyError:  # tem has probably been KO'd
            return None

    def _check_win(self, sides=(0, 1)):
        # TODO: consider situation where all remaining tems faint
        # simultaneously - should I use speed arrow here?
        for side in sides:
            if all(tem.fainted for tem in self.teams[side]):
                self.winner = other(side)
                return True

        return False

    def _active_tems_by_speed(self):
        # TODO: handle plethoric, last rush
        tem_speeds = {}
        for side in (0, 1):
            for field_slot, tem_slot in enumerate(self.active[side]):
                tem_speeds[(side, tem_slot)] = (
                    self.teams[side][tem_slot].live_stats[Stats.Spe],
                    side == self.speed_arrow,
                    field_slot,
                )

        yield from sorted(tem_speeds, key=lambda pos: tem_speeds[pos])

    def _actions_gen(self, choices):
        from collections import defaultdict

        # TODO: handle plethoric, last rush
        attacks = defaultdict(
            lambda: {'priority': 0},
            {choice.detail: lookup_attack(choice.detail) for choice in choices},
        )
        moves = {
            (side, tem): choice.priority(
                self.active_tem(side, tem), attacks[choice.detail]['priority']
            )
            for side, side_choices in enumerate(choices)
            for tem, choice in enumerate(side_choices)
        }
        priorities = {
            prio: [slot for slot in moves if moves[slot] == prio]
            for prio in set(moves.values())
        }

        for prio in sorted(priorities):
            tems = priorities[prio]
            arrow_tems = [tem for tem in tems if tem[0] == self.speed_arrow]
            non_arrow_tems = [tem for tem in tems if tem[0] != self.speed_arrow]
            if arrow_tems and non_arrow_tems:
                self.speed_arrow = other(self.speed_arrow)

            # sorted ensures left tem moves first, which I guess is correct?
            yield from sorted(arrow_tems)
            yield from sorted(non_arrow_tems)

    def _fix_attack_targetting(self, side, tem_slot, choice):
        '''
        A few things need to be fixed with targetting before a move is used.
        First, if the target tems are KO'd, we need to choose new targets, or
        not use the move.
        Then, we need to work out which secondary targets are hit by 'clockwise'
        targetting (e.g. chain lightning)
        '''
        # First, handle KO'd targets
        if all(self.active[side_][slot] for side_, slot in choice.target):
            orig_targ = choice.target[0]
            if (
                choice.detail['target'] in {'single', 'clockwise', 'other'}
                and orig_targ[0] != side
                and self.active[orig_targ[0]][other(orig_targ[1])] is not None
            ):
                choice.target = ((orig_targ[0], other(orig_targ[1])))
            else:
                # No remaining targets for the move
                return False

        # Work out all targets for 'clockwise' targetting
        def next_tem_clockwise(battle, side, tem_slot):
            ordering = (
                (side, 1), (other(side), 0), (other(side), 1), (side, 0), (side, 1)
            )
            for side, slot in ordering[tem_slot:]:
                if battle.active[side][slot] is not None:
                    return (side, slot)

        if choice.detail['target'] == 'clockwise':
            next_tem = choice.target[0]
            choice.target = [next_tem]
            for _ in range(2):
                next_tem = next_tem_clockwise(self, *next_tem)
                choice.target.append(next_tem)

        return True

    def _handle_switchin_traits(self, switchin, side):
        if switchin.trait == 'Demoralize':
            for tem_slot in self.active[other(side)]:
                self.teams[other(side)][tem_slot].apply_boost(Stats.Spe, -1)
        elif switchin.trait == 'Protector' and switchin.ally:
            switchin.ally.apply_boost(Stats.Def)
            switchin.ally.apply_boost(Stats.SpD)
        if (
            Types.digital in switchin.types
            and switchin.ally and switchin.ally.trait == 'Fast Charge'
        ):
            switchin.ally.apply_boost(Stats.Spe, 2)

    def _process_switch(self, side, tem_slot, choice):
        switcher = self.active_tem(side, tem_slot)
        if switcher.trapped:
            return
        target = self.teams[side][choice.target]
        if (ally := switcher.ally) is not None:
            ally.ally = target
        self.active[side][tem_slot] = choice.target

        self._handle_switchin_traits(target, side)

    def _handle_ko(self, tem, side, tem_slot):
        tem.fainted = True
        if (ally := tem.ally) is not None:
            ally.ally = None
        del self.active[side][tem_slot]

    def _process_attack(self, side, tem_slot, choice):
        from contextlib import suppress
        from calc import trait_modifiers, gear_modifiers, calc_damage

        attacker = self.active_tem(side, tem_slot)
        attack = attacker.lookup_attack(choice.detail)
        if not self._fix_attack_targetting(side, tem_slot, choice):
            # No remaining targets for the move - just return
            return

        attacker.use_stamina(attack['stamina'])

        # Deal damage
        clockwise_mod = 1.0
        targets = []
        for target_side, tem in choice.target:
            target = self.active_tem(target_side, tem)
            targets.append(target)
            if attack['class'] != 'Status':
                trait_mod = trait_modifiers(attacker, attack, target)
                gear_mod = gear_modifiers(attacker, attack, target)
                total_mod = trait_mod * gear_mod * clockwise_mod
                damage = calc_damage(attacker, attack, target, total_mod)
                target.take_damage(damage)
            for effect, num in attack['effects'].items():
                if effect in Statuses:
                    target.apply_status(effect, num)
                elif effect in Stats:
                    target.apply_boost(effect, num)
                else:
                    # TODO: weird effects like strangle
                    raise NotImplementedError()
            if attack['target'] == 'clockwise':
                with suppress(NameError):
                    if damage <= 0:
                        # stop chaining if no damage e.g. electric synthesize
                        break
                    clockwise_mod = 0.7 if clockwise_mod == 1.0 else 0.6

            target.post_hit(attacker, attack)

        for effect, num in attack['self'].items():
            if effect in Statuses:
                attacker.apply_status(effect, num)
            elif effect == Stats.HP:
                # This is for recoil / healing moves. The `num` represents
                # fraction of hp gained (so -1 == ko yourself).
                if num > 0:
                    num = floor(attacker.stats[Stats.HP] * num)
                else:
                    num = ceil(attacker.stats[Stats.HP] * num)
                attacker.take_damage(num)
            elif effect in Stats:
                attacker.apply_boost(effect, num)
            else:
                # There aren't any non-standard self effects yet
                raise RuntimeError(
                    f'Attack {attack["name"]} used by {attacker.species} has '
                    f'unrecognised effect {effect}.'
                )
        attacker.post_attack(attack)

        if attacker.live_stats[Stats.HP] <= 0:
            if attacker.trait == 'Wrecked Farewell':
                for target in targets:
                    # TODO: confirm this should use floor()
                    target.take_damage(target.stats[Stats.HP] // 4)
            self._handle_ko(attacker)
        for target in targets:
            if target.live_stats[Stats.HP] <= 0:
                self._handle_ko(target)

    def process_turn(self, choices):
        # Start-of-turn effects
        for side, tem_slot in self._active_tems_by_speed():
            (tem := self.teams[side][tem_slot]).start_turn()
            if tem.fainted and self._check_win(sides=(side,)):
                return
        # First, run actions that result from choices
        for side, tem_slot in self._actions_gen(choices):
            choice = choices[side][tem_slot]

            if choice.action == 'run':
                raise NotImplementedError()
            elif choice.action == 'item':
                raise NotImplementedError()
            elif choice.action == 'switch':
                self._process_switch(choice, side, tem_slot, choice)
            elif choice.action == 'rest':
                raise NotImplementedError()
            else:
                self._process_attack(choice, side, tem_slot, choice)

            if self._check_win():
                return

        # End-of-turn effects
        for side, tem_slot in self._active_tems_by_speed():
            (tem := self.teams[side][tem_slot]).end_turn()
            if tem.fainted and self._check_win(sides=(side,)):
                return

        # Finally, replace tems that fainted
        raise NotImplementedError()


def other(x, /):
    ''' Improves readability for e.g. other(side), other(tem_slot) '''
    return 1 - x
