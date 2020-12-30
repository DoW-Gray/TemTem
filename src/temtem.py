# vim: set fileencoding=utf-8 :
"""
temtem.py: TemTem class and associated functions
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

import os

from math import ceil, floor

from .static import (
    Stats,
    Types,
    Statuses,
    STAT_CONSTS,
    DEFAULT_LEVEL,
    STATUS_CATCH_BONUS,
    lookup_temtem_data,
    lookup_attack,
)

from typing import Iterable, Dict, Any

import logging
log = logging.getLogger(__name__)

SAMPLE_SETS = os.path.join('data', 'sets.txt')


class TemTem:
    def __init__(
            self,
            species: str,
            moves: Iterable[str] = [],
            trait: str = '',
            svs: Dict[str, int] = {},
            tvs: Dict[str, int] = {},
            gear: str = '',
            level: int = DEFAULT_LEVEL,
    ):
        from .traits import lookup_trait
        from .gear import lookup_gear

        self.species = species
        self.moves = {move: 0 for move in moves}  # {move: hold counter}
        self.trait = lookup_trait(trait)
        base_tem_data = lookup_temtem_data(species)
        self.base_stats = base_tem_data['Stats']
        self.types = base_tem_data['Types']
        self.level = int(level)

        self.svs = {}
        self.tvs = {}
        for stat in Stats:
            if stat.name in svs:
                self.svs[stat] = int(svs[stat.name])
            elif stat in svs:
                self.svs[stat] = int(svs[stat])
            else:
                self.svs[stat] = 50
            if stat.name in tvs:
                self.tvs[stat] = int(tvs[stat.name])
            elif stat in tvs:
                self.tvs[stat] = int(tvs[stat])
            else:
                self.tvs[stat] = 0
        self._calc_stats()
        self.HP = self.stats[Stats.HP]  # current hp
        self.Sta = self.stats[Stats.Sta]  # current sta

        self.gear = lookup_gear(gear)
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}

        self.statuses = {}
        self.resting = False
        self.overexerted = 0
        # we can't just use a bool for overexerted, because there's one turn
        # the tem uses too much sta, then one turn it can't move, so two
        # non-normal states we need to represent at end of turn.
        # So use 2 = used too much sta this turn, 1 = overexerted, 0 = normal
        self.fainted = False
        self.trait_counter = 0  # meaning is trait-specific

        self.ally = None

    def __repr__(self) -> str:
        return f'<TemTem {self.species}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, TemTem):
            return NotImplemented

        return (
            self.species == other.species
            and set(self.moves) == set(other.moves)
            # cast to set because move order and hold aren't important
            and self.trait == other.trait
            and self.svs == other.svs
            and self.tvs == other.tvs
            and self.gear == other.gear
            and self.level == other.level
            and self.boosts == other.boosts
        )

    # private stat calculation funcs

    def _calc_stat(self, stat: Stats) -> int:
        """
        Separated out into its own function for e.g. increasing one tv
        """
        val1 = 1.5 * self.base_stats[stat] + self.svs[stat] + self.tvs[stat] / 5
        val1 = (val1 * self.level) // STAT_CONSTS[stat][0]
        val2 = self.svs[stat] * self.base_stats[stat] * self.level
        val2 //= STAT_CONSTS[stat][1]
        const = STAT_CONSTS[stat][2] + (self.level if stat == Stats.HP else 0)
        return int(val1 + val2 + const)

    def _calc_stats(self):
        stats = {}
        for stat in Stats:
            stats[stat] = self._calc_stat(stat)
        self.stats = stats

    def _live_stat(self, stat: Stats) -> int:
        if stat in (Stats.HP, Stats.Sta):
            raise ValueError(f"{self!r}._live_stat() called for stat {stat}")

        res = self.stats[stat]
        if (boost := self.boosts[stat]) > 0:
            res *= (2 + boost) / 2
        elif boost:
            res *= 2 / (2 - boost)

        if stat in (Stats.Atk, Stats.SpA) and self.burned:
            res *= 0.7

        # TODO: trait stat boosts, such as settling? I'll need to test in-game

        return max(1, int(res))

    # public funcs for use in simulating battles

    def clear_boosts(self):
        # TODO: check if determined applies here
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}

    def apply_boost(self, stat: Stats, boost: int):
        from .traits import Determined, Guardian

        if boost < 0 and (
            self.trait is Determined or
            (self.ally is not None and self.ally.trait is Guardian)
        ):
            return

        self.boosts[stat] = max(-5, min(5, self.boosts[stat] + boost))

    def apply_status(self, status: Statuses, turns: int):
        from contextlib import suppress
        from .effects import DontApplyStatus

        # TODO: check gear applies before trait
        if not self.seized:
            gear_effect = self.gear.on_status(self, status, turns)
            try:
                gear_effect.apply(target=self)
            except DontApplyStatus:
                return

        trait_effect = self.trait.on_status(self, status, turns)
        try:
            trait_effect.apply(target=self)
        except DontApplyStatus:
            return

        if self.ally is not None:
            ally_effect = self.ally.trait.on_ally_status(
                self.ally, self, status, turns
            )
            try:
                ally_effect.apply(target=self.ally, ally=self)
            except DontApplyStatus:
                return

        # Check if a type or current status changes what's being applied
        if status in self.statuses:
            if status != Statuses.cold:
                return
            self.statuses[Statuses.frozen] = self.statuses[Statuses.cold]
            del self.statuses[Statuses.cold]

        elif status == Statuses.cold:
            if self.frozen:
                return
            with suppress(KeyError):
                del self.statuses[Statuses.burned]

        elif status == Statuses.burned:
            if Types.fire in self.types:
                return
            with suppress(KeyError):
                del self.statuses[Statuses.cold]
            with suppress(KeyError):
                del self.statuses[Statuses.frozen]

        elif status == Statuses.asleep:
            if Types.mental in self.types:
                return
            if self.alerted:
                return

        elif status == Statuses.poisoned:
            if Types.toxic in self.types:
                return

        elif status == Statuses.exhausted:
            if self.vigorized:
                del self.statuses[Statuses.vigorized]
                return

        elif status == Statuses.vigorized:
            if self.exhausted:
                del self.statuses[Statuses.exhausted]
                return

        # Handle applying a status when there are already 2
        if len(self.statuses) == 2:
            # remove oldest status to replace with new status condition
            del self.statuses[
                sorted(self.statuses, key=lambda x: self.statuses[x]['existed'])[0]
            ]

        self.statuses[status] = {'remaining': turns, 'existed': 0}

    def start_turn(self):
        '''
        Handle all effects that occur at the start of each turn.
        '''
        if not self.seized:
            self.gear.on_turn_start(self).apply(target=self)
        self.trait.on_turn_start(self).apply(target=self)

    def end_turn(self, active: bool = False):
        '''
        handle various things that need to be done at the end of each turn:
          - status effects update / run out
          - handle stamina regeneration and overexertion
        '''
        # update status conditions
        new_statuses = {}
        apply_alerted = False
        for status, details in self.statuses.items():
            if status == Statuses.poisoned:
                self.take_damage(ceil(self.max_hp / 8))
            elif status == Statuses.burned:
                self.take_damage(ceil(self.max_hp / 16))
            elif status == Statuses.regenerated:
                self.take_damage(floor(self.max_hp / 10))
            elif status == Statuses.doomed and details['remaining'] == 1:
                # TODO: do I want a different "become KO'd" method?
                self.take_damage(self.max_hp)

            if details['remaining'] > 1:
                new_statuses[status] = {
                    'remaining': details['remaining'] - 1,
                    'existed': details['existed'] + 1,
                }
            elif status == Statuses.asleep:
                apply_alerted = True

        self.statuses = new_statuses
        if apply_alerted:
            self.apply_status(Statuses.alerted, 1)

        if not self.seized:
            self.gear.on_turn_end(self).apply(target=self)
        self.trait.on_turn_end(self).apply(target=self)

        # update overexertion
        if self.overexerted:
            self.overexerted -= 1

        # update stamina
        sta = self.max_sta
        denom = 5 if self.resting else 20
        self.Sta = min(self.max_sta, int(sta + 1 + ceil(sta / denom)))
        self.resting = False
        # NOTE: trait/gear .on_rest method is handled elsewhere, before this point.

        # Effects that only happen if the tem is on the field
        if not active:
            return

        # update hold counts
        for move, hold in self.moves.items():
            self.moves[move] = min(hold + 1, lookup_attack(move)['hold'])

    def take_damage(self, damage: int):
        '''
        take damage or heal
        Note: trait / gear .on_take_damage is handled before this point
        '''
        if self.fainted or not damage:
            return

        assert isinstance(damage, int)

        self.HP -= damage

        if self.HP <= 0:
            self.fainted = True
            self.HP = 0
        elif self.HP > self.max_hp:
            # can't heal above max HP
            self.HP = self.max_hp

        # TODO: handle waking up, soft touch

    def use_stamina(self, stamina: int):
        from .traits import Resiliant, Tireless, Vigorous

        if self.vigorized:
            stamina //= 2  # TesTem uses floor here
        elif self.exhausted:
            stamina = floor(stamina * 1.5)  # TesTem uses floor here

        if self.Sta >= stamina:
            self.Sta -= stamina
            return

        damage = stamina - self.Sta
        if self.trait is Resiliant:
            damage = min(damage, self.HP - 1)
        self.take_damage(damage)
        self.Sta = 0

        if self.trait is not Tireless:
            self.overexerted = 2
            if self.trait is Vigorous:
                self.trait_counter = 1

    def lookup_attack(self, atk_name: str) -> Dict[str, Any]:
        '''
        Return the atk dict given by static.lookup_attack, but with fixed
        synergy (e.g. from KOs or switches), and handle a few other things
        like Shuine's Horn.
        '''
        from copy import copy
        from .gear import ShuinesHorn

        attack = lookup_attack(atk_name)
        if 'synergy type' in attack:
            syn_type = attack['synergy type']
            if self.ally and syn_type in self.ally.types:
                attack = lookup_attack(f'{attack["name"]} +{syn_type.detail}')
        elif 'synergy attack' in attack:
            synergy_type = attack['name'].split(' +')[1]
            if (
                (not self.ally)
                or Types[synergy_type] not in self.ally.types
            ):
                attack = lookup_attack(attack['name'].split(' +')[0])

        if (
            attack['type'] == Types.toxic
            and self.gear is ShuinesHorn
            and not self.seized
        ):
            attack = copy.copy(attack)
            # Don't need copy.deepcopy, as we only change a top-level
            # property (type)
            attack['type'] = Types.water

        return attack

    def catch_chance(self, card_rate: int = 1, four_leaf_clover: bool = False) -> float:
        """
        See: https://temtem.gamepedia.com/Taming#Capture_formula
        Variable names here are pretty meaningless, but at least match those
        in the above webpage.
        """
        from math import sqrt

        a = lookup_temtem_data(self.species)['Catch Rate'] * card_rate
        a *= (4 * self.max_hp - 3 * self.HP)
        for status in self.statuses:
            a *= STATUS_CATCH_BONUS[status]
        a /= (2 * self.max_hp + 10 * self.level)
        a *= 1.1 if four_leaf_clover else 1

        b = 1_000_000 / sqrt(sqrt(21_000_000 / a))
        if b >= 50_000:
            return 1.0
        return (b / 50_000) ** 4

    # methods to access important info about the tem

    # stats

    @property
    def max_hp(self) -> int:
        return self.stats[Stats.HP]

    @property
    def max_sta(self) -> int:
        return self.stats[Stats.Sta]

    @property
    def Spe(self) -> int:
        return self._live_stat(Stats.Spe)

    @property
    def Atk(self) -> int:
        return self._live_stat(Stats.Atk)

    @property
    def Def(self) -> int:
        return self._live_stat(Stats.Def)

    @property
    def SpA(self) -> int:
        return self._live_stat(Stats.SpA)

    @property
    def SpD(self) -> int:
        return self._live_stat(Stats.SpD)

    # status conditions

    @property
    def cold(self):
        return Statuses.cold in self.statuses

    @property
    def frozen(self):
        return Statuses.frozen in self.statuses

    @property
    def asleep(self):
        return Statuses.asleep in self.statuses

    @property
    def trapped(self):
        return Statuses.trapped in self.statuses

    @property
    def doomed(self):
        return Statuses.doomed in self.statuses

    @property
    def seized(self):
        return Statuses.seized in self.statuses

    @property
    def poisoned(self):
        return Statuses.poisoned in self.statuses

    @property
    def burned(self):
        return Statuses.burned in self.statuses

    @property
    def exhausted(self):
        return Statuses.exhausted in self.statuses

    @property
    def vigorized(self):
        return Statuses.vigorized in self.statuses

    @property
    def immune(self):
        return Statuses.immune in self.statuses

    @property
    def regenerated(self):
        return Statuses.regenerated in self.statuses

    @property
    def nullified(self):
        return Statuses.nullified in self.statuses

    @property
    def evading(self):
        return Statuses.evading in self.statuses

    @property
    def alerted(self):
        return Statuses.alerted in self.statuses

    @property
    def exiled(self):
        return Statuses.exiled in self.statuses

    # import / export functions

    @classmethod
    def from_importable(cls, importable: str) -> "TemTem":
        """
        e.g.
        Top Percentage (Rattata) @ Example Item
        Trait: Resistant
        Level: 48
        TVs: 500 Spe / 500 Atk
        SVs: 0 SpA
        - Hi Jump Kick
        - Falcon Punch
        - Tombstoner
        - DDoS
        """

        def line_iter(importable: str) -> Iterable[str]:
            if isinstance(importable, str):
                importable = importable.split('\n')

            for line in importable:
                yield line

        lines = line_iter(importable)

        while not (line := next(lines)).strip():
            pass  # strip leading blank lines

        # line 1: nickname (species) @ gear
        if '@' in line:
            parts = line.strip().split('@')
            gear = parts[1].strip() or None
            line = parts[0]
        else:
            gear = None

        if '(' in line:
            parts = line.split('(')
            species = parts[1].split(')')[0].strip()
        else:
            species = line.strip()

        # next lines: trait, level, tvs, svs
        tvs = {stat: 0 for stat in Stats}
        svs = {stat: 50 for stat in Stats}
        level = DEFAULT_LEVEL
        while not (line := next(lines).strip()).startswith('-'):
            if line.startswith('Trait:'):
                trait = line.split('Trait:')[1].strip()
            elif line.startswith('Level:'):
                level = int(line.split('Level:')[1].strip())
            elif line.startswith('Luma:'):
                pass  # don't care about luma
            else:
                assert line[1:4] == 'Vs:'
                vals = tvs if line.startswith('TVs:') else svs
                for part in line.split(':')[1].split('/'):
                    num, stat = part.strip().split()
                    vals[Stats[stat]] = int(num)

        # Now for moves
        moves = [line.lstrip('-').strip()]
        for line in lines:
            if not line.startswith('-'):
                break  # ignore lines after the final move
            moves.append(line.lstrip('-').strip())

        return cls(species, moves, trait, svs, tvs, gear, level)

    def export(self) -> str:
        res = f'{self.species} {f"@ {self.gear.__name__}" or ""}\n'
        res += f'Trait: {self.trait.__name__}\n'
        if self.level != DEFAULT_LEVEL:
            res += f'Level: {self.level}\n'

        tvs = ' / '.join(
            f'{val} {stat.name}' for stat, val in self.tvs.items() if val
        )
        if tvs:
            res += f'TVs: {tvs}\n'
        svs = ' / '.join(
            f'{val} {stat.name}' for stat, val in self.svs.items() if val != 50
        )
        if svs:
            res += f'SVs: {svs}\n'

        for move in self.moves:
            res += f'- {move}\n'

        return res


def gen_tems(inpt: str) -> Iterable[TemTem]:
    if isinstance(inpt, str):
        inpt = inpt.split('\n')

    def try_yield_tem(next_tem):
        try:
            return TemTem.from_importable(next_tem)
        except Exception as err:
            log.error('Unable to parse the following lines:')
            for line in next_tem:
                log.error(line)
            log.error('Saw the following exception: %r', err)

    next_tem = []
    for line in inpt:
        if not line.strip():
            if next_tem:
                if tem := try_yield_tem(next_tem):
                    yield tem
                next_tem = []
        else:
            next_tem.append(line)

    if next_tem:
        try_yield_tem(next_tem)


# Tests
def test_temtem_class():
    from .test_data import (
        GYALIS_IMPORT,
        GYALIS_STATS,
        GYALIS_TEM,
        KINU_IMPORT,
        KINU_TEM,
    )

    # test stat calculation
    assert GYALIS_TEM.stats == GYALIS_STATS

    # test boost application and TemTem._live_stat
    GYALIS_TEM.apply_boost(Stats.Atk, 2)
    assert GYALIS_TEM.Atk == 302
    GYALIS_TEM.apply_boost(Stats.Atk, 1)
    assert GYALIS_TEM.Atk == 377
    GYALIS_TEM.apply_boost(Stats.Def, -6)
    assert GYALIS_TEM.boosts[Stats.Def] == -5
    assert GYALIS_TEM.Def == 23
    GYALIS_TEM.clear_boosts()
    assert {
        Stats.HP: GYALIS_TEM.max_hp,
        Stats.Sta: GYALIS_TEM.max_sta,
        Stats.Spe: GYALIS_TEM.Spe,
        Stats.Atk: GYALIS_TEM.Atk,
        Stats.Def: GYALIS_TEM.Def,
        Stats.SpA: GYALIS_TEM.SpA,
        Stats.SpD: GYALIS_TEM.SpD,
    } == GYALIS_STATS

    # TODO: test apply_status, end_turn, take_damage, use_stamina

    # test TemTem.export
    assert GYALIS_TEM.export() == GYALIS_IMPORT

    # test TemTem.from_importable
    gyalis_import = TemTem.from_importable(GYALIS_IMPORT)
    kinu_import = TemTem.from_importable(KINU_IMPORT)
    for imported, tem in ((gyalis_import, GYALIS_TEM), (kinu_import, KINU_TEM)):
        assert imported == tem
        assert imported.stats == tem.stats
        assert imported.moves == tem.moves
        assert imported.gear == tem.gear
        assert imported.trait == tem.trait
        assert imported.level == tem.level


def test_gen_tems():
    from .test_data import MULTI_IMPORT, GYALIS_TEM, KINU_TEM

    with open(SAMPLE_SETS, 'r') as fp:
        next(gen_tems(fp))

    gen = gen_tems(MULTI_IMPORT)
    assert next(gen) == GYALIS_TEM
    assert next(gen) == KINU_TEM
