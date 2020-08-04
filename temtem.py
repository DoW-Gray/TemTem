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

from static import (
    Stats,
    Types,
    Statuses,
    STAT_CONSTS,
    DEFAULT_LEVEL,
    STATUS_ITEMS,
    lookup_temtem_data,
    lookup_attack,
)

from log import error

SAMPLE_SETS = os.path.join('data', 'sets.txt')


class TemTem:
    def __init__(
            self,
            species,
            moves,
            trait,
            svs={},
            tvs={},
            gear=None,
            level=DEFAULT_LEVEL
    ):
        self.species = species
        self.moves = moves
        self.trait = trait
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

        self.gear = gear
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}
        self._calc_live_stats()

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

    def __repr__(self):
        return "<TemTem %s>" % self.species

    def __eq__(self, other):
        if not isinstance(other, TemTem):
            return NotImplemented

        return (
            self.species == other.species
            and set(self.moves) == set(other.moves)  # order isn't relevant
            and self.trait == other.trait
            and self.svs == other.svs
            and self.tvs == other.tvs
            and self.gear == other.gear
            and self.level == other.level
            and self.boosts == other.boosts
        )

    def _calc_stat(self, stat):
        """
        Separated out into its own function for e.g. increasing one tv
        """
        val1 = 1.5 * self.base_stats[stat] + self.svs[stat] + self.tvs[stat] / 5
        val1 = (val1 * self.level) // STAT_CONSTS[stat][0]
        val2 = self.svs[stat] * self.base_stats[stat] * self.level
        val2 //= STAT_CONSTS[stat][1]
        const = STAT_CONSTS[stat][2] + (self.level if stat == Stats.HP else 0)
        return int(val1 + val2 + const)

    # private stat calculation funcs

    def _calc_stats(self):
        stats = {}
        for stat in Stats:
            stats[stat] = self._calc_stat(stat)
        self.stats = stats

    def _calc_live_stats(self):
        live_stats = {}
        for stat in Stats:
            if stat in (Stats.HP, Stats.Sta):
                try:
                    live_stats[stat] = self.live_stats[stat]
                except (KeyError, AttributeError):
                    live_stats[stat] = self.stats[stat]
            elif (boost := self.boosts[stat]) > 0:
                live_stats[stat] = int(self.stats[stat] * (2 + boost) / 2)
            elif boost < 0:
                live_stats[stat] = max(1, int(2 * self.stats[stat] / (2 - boost)))
            else:
                live_stats[stat] = self.stats[stat]
        self.live_stats = live_stats

    # public funcs for use in simulating battles

    def clear_boosts(self):
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}
        self.live_stats = self.stats

    def apply_boost(self, stat, boost):
        # TODO: check for determined trait

        if isinstance(stat, str):
            stat = Stats[stat]

        self.boosts[stat] += boost
        if self.boosts[stat] > 5:
            self.boosts[stat] = 5
        elif self.boosts[stat] < -5:
            self.boosts[stat] = -5

        self._calc_live_stats()

    def apply_status(self, status, turns):
        from contextlib import suppress

        if self.trait == 'Neutrality':
            return

        if isinstance(status, str):
            status = Statuses[status]

        with suppress(KeyError):
            if self.gear == STATUS_ITEMS[status] and self.seized:
                return

        # TODO: check if a tem can have both vigorized and exhausted at once

        if status in self.statuses:
            if status != Statuses.cold:
                return
            self.statuses[Statuses.frozen] = self.statuses[Statuses.cold]
            del self.statuses[Statuses.cold]
            if self.trait == 'Fever Rush':
                # There's definitely a better way of doing this
                self.apply_boost(Stats.Atk, 1)
                return

        elif status == Statuses.cold:
            if self.frozen:
                return
            if self.trait in ('Mucous', 'Warm-Blooded'):
                return
            if self.trait == 'Cold-Natured':
                status = Statuses.frozen
            if self.ally and self.ally.trait == 'Guardian':
                # TODO: check if guardian stops frozen on a cold-natured ally
                return

            with suppress(KeyError):
                del self.statuses[Statuses.burned]

        elif status == Statuses.burned:
            if Types.fire in self.types:
                return
            if self.ally and self.ally.trait == 'Guardian':
                return

            with suppress(KeyError):
                del self.statuses[Statuses.cold]
                del self.statuses[Statuses.frozen]

        elif status == Statuses.asleep:
            if Types.mental in self.types:
                return
            if self.alerted:
                return
            if self.trait == 'Caffeinated':
                return
            if self.trait == 'Zen':
                self.apply_boost(Stats.Def, 1)
                self.apply_boost(Stats.SpD, 1)
        elif status == Statuses.poisoned:
            if Types.toxic in self.types:
                return
            if self.trait == 'Mithridatism':
                return
            if self.ally and self.ally.trait == 'Guardian':
                return

        if self.trait == 'Fever Rush':
            self.apply_boost(Stats.Atk, 1)

        if len(self.statuses) == 2:
            # remove oldest status to replace with new status condition
            del self.statuses[
                sorted(self.statuses, key=lambda x: self.statuses[x]['existed'])[0]
            ]

        if self.trait == 'Receptive' and status in {
            Statuses.vigorized,
            Statuses.regenerated,
            Statuses.evading,
            Statuses.alerted,
        }:  # TODO: check if Immune is also boosted
            turns += 1
        elif self.trait == 'Resistant' and status in {
            Statuses.cold,
            Statuses.frozen,
            Statuses.asleep,
            Statuses.trapped,
            Statuses.poisoned,
            Statuses.burned,
            Statuses.exhausted,
        }:
            turns -= 1
            if not turns:
                # Based on what data I have, this logic seems to come after
                # removing the oldest status if there's 2 already
                return

        # TODO: handle receptive and resistant traits
        self.statuses[status] = {'remaining': turns, 'existed': 0}

    def start_turn(self):
        '''
        Handle various things that need to be done at the start of each turn.
        '''
        if self.asleep and self.gear == 'Pillow' and not self.seized:
            # TODO: check that `floor` is correct here
            self.take_damage(-floor(self.stats[Stats.HP] / 10))

        if self.gear == 'Sweatband' and not self.seized:
            max_sta = self.stats[Stats.sta]
            self.live_stats[Stats.sta] = min(floor(max_sta * 1.15), max_sta)

    def end_turn(self):
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
                self.take_damage(ceil(self.stats[Stats.HP] / 8))
            elif status == Statuses.burned:
                self.take_damage(ceil(self.stats[Stats.HP] / 16))
            elif status == Statuses.regenerated:
                self.take_damage(floor(self.stats[Stats.HP] / 10))
            elif status == Statuses.doomed and details['remaining'] == 1:
                # TODO: do I want a different "become KO'd" method?
                self.take_damage(self.stats[Stats.HP])

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

        # TODO: check this is the right place to check energy reserve
        if (
            self.trait == 'Energy Reserve'
            and self.live_stats[Stats.HP] < self.stats[Stats.HP] / 4
        ):
            self.apply_status(Statuses.vigorized, 2)

        # update overexertion
        if self.overexerted:
            self.overexerted -= 1

        # update stamina
        live_sta = self.live_stats[Stats.Sta]
        sta = self.stats[Stats.sta]
        denom = 5 if self.resting else 20
        self.live_stats[Stats.Sta] = min(sta, live_sta + 1 + ceil(sta / denom))
        self.resting = False

        # TODO: various other effects like energy reserve trait

    def take_damage(self, damage):
        '''
        take damage or heal
        '''
        if self.fainted or not damage:
            return

        assert isinstance(damage, int)

        self.live_stats[Stats.HP] -= damage

        if self.live_stats[Stats.HP] <= 0:
            self.fainted = True
            self.live_stats[Stats.HP] = 0
        elif self.live_stats[Stats.HP] > self.stats[Stats.HP]:
            # can't heal above max HP
            self.live_stats[Stats.HP] = self.stats[Stats.HP]

        # TODO: handle benefactor trait
        # TODO: handle waking up, soft touch

    def use_stamina(self, stamina):
        if self.vigorized:
            stamina //= 2  # TesTem uses floor here
        if self.exhausted:
            # TODO: if can't be exhausted and vigorized, should be elif
            stamina = floor(stamina * 1.5)  # TesTem uses floor here

        if self.live_stats[Stats.Sta] > stamina:
            self.live_stats[Stats.Sta] -= stamina
            return

        damage = stamina - self.live_stats[Stats.Sta]
        if self.trait == 'Resilient':
            damage = min(damage, self.live_stats[Stats.HP] - 1)
        self.take_damage(damage)
        self.live_stats[Stats.Sta] = 0

        if self.trait != 'Tireless':
            self.overexerted = 2

    def lookup_attack(self, atk_name):
        '''
        Return the atk dict given by static.lookup_attack, but with fixed
        synergy (e.g. from KOs or switches), and handle a few other things
        like Shuine's Horn.
        '''
        from copy import copy

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
            and self.gear == 'Shuine\'s Horn'
            and not self.seized
        ):
            attack = copy.copy(attack)
            # Don't need copy.deepcopy, as we only change a top-level
            # property (type)
            attack['type'] = Types.water

        return attack

    def post_attack(self, attack):
        if self.trait == 'Aerobic' and attack['type'] == Types.wind:
            self.apply_boost(Stats.Spe, 1)
            self.apply_boost(Stats.SpD, -1)
        elif self.trait == 'Anaerobic' and attack['type'] == Types.toxic:
            self.apply_boost(Stats.SpD, 1)
            self.apply_boost(Stats.SpA, -1)
        elif self.trait == 'Patient' and attack['hold']:
            max_sta = self.stats[Stats.Sta]
            self.live_stats[Stats.Sta] = min(
                max_sta, self.live_stats[Stats.Sta] + max_sta // 10
            )
        elif self.trait == 'Rejuvenate' and attack['status'] == 'Physical':
            self.take_damage(-floor(self.stats[Stats.HP] * 0.15))

    def post_hit(self, attacker, attack, damage):
        if self.trait == 'Amphibian' and attack['type'] == Types.water:
            self.apply_boost(Stats.Spe, 1)
        elif self.trait == 'Callosity' and attack['class'] == 'Physical':
            self.apply_boost(Stats.Def, 1)
        elif self.trait == 'Fainted Curse' and self.live_stats[Stats.HP] <= 0:
            attacker.take_damage(floor(attacker.stats[Stats.HP] * 0.4))
        elif self.trait == 'Mirroring' and damage > 0:
            attacker.take_damage(damage // 5)
        elif (
            self.trait == 'Provident'
            and attack['type'] in (Types.fire, Types.earth, Types.melee)
        ):
            self.apply_boost(Stats.SpD, 1)
        elif self.trait == 'Toxic Farewell' and self.live_stats[Stats.HP] <= 0:
            attacker.apply_status(Statuses.poisoned, 3)
        elif self.trait == 'Toxic Skin' and attack['class'] == 'Physical':
            attacker.apply_status(Statuses.poisoned, 2)
        elif (
            self.trait == 'Trance'
            and self.live_stats[Stats.HP] < self.stats[Stats.HP] / 3
        ):
            self.apply_status(Statuses.asleep, 2)
            self.apply_status(Statuses.regenerated, 2)
            self.apply_boost(Stats.SpA, 2)
            self.apply_boost(Stats.SpD, 2)
        elif self.trait == 'Trauma':
            if attack['class'] == 'Physical':
                self.apply_boost(Stats.Def, -1)
            elif attack['class'] == 'Special':
                self.apply_boost(Stats.SpD, -1)

        if attacker.trait == 'Apothecary' and attack['class'] == 'Special':
            if attacker is self.ally:
                self.apply_status(Statuses.regenerated, 1)
            else:
                self.apply_status(Statuses.poisoned, 1)
        elif attacker.trait == 'Tri-Apothecary' and attack['class'] == 'Special':
            if attacker is self.ally:
                self.apply_status(Statuses.regenerated, 3)
            else:
                self.apply_status(Statuses.poisoned, 3)
        elif attacker.trait == 'Prideful' and self.live_stats[Stats.HP] <= 0:
            attacker.apply_boost(Stats.Atk, 1)
            attacker.apply_boost(Stats.SpA, 1)
            attacker.apply_boost(Stats.Spe, 1)

        if self.ally and self.ally.trait == 'Benefactor' and damage > 0:
            self.ally.take_damage(self.ally.stats[Stats.HP] // 10)

        if self.asleep and attacker.trait != 'Soft Touch':
            # TODO: wake up, handling alerted
            raise NotImplementedError()

    # shorthand methods to check statuses

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
    def from_importable(cls, importable):
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

        def line_iter(importable):
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
        level = 48
        while not (line := next(lines).strip()).startswith('-'):
            if line.startswith('Trait:'):
                trait = line.split('Trait:')[1].strip()
            elif line.startswith('Level:'):
                level = int(line.split('Level:')[1].strip())
            elif line.startswith('Luma:'):
                pass  # don't care about luma
            else:
                assert line[1:4] == 'Vs:'
                vs = tvs if line.startswith('TVs:') else svs
                for part in line.split(':')[1].split('/'):
                    num, stat = part.strip().split()
                    vs[Stats[stat]] = int(num)

        # Now for moves
        moves = [line.lstrip('-').strip()]
        for line in lines:
            if not line.startswith('-'):
                break  # ignore lines after the final move
            moves.append(line.lstrip('-').strip())

        return cls(species, moves, trait, svs, tvs, gear, level)

    def export(self):
        res = '%s %s\n' % (self.species, '@ %s' % (self.gear or ''))
        res += 'Trait: %s\n' % self.trait
        if self.level != DEFAULT_LEVEL:
            res += 'Level: %s\n' % self.level

        tvs = ' / '.join(
            '%d %s' % (val, stat.name) for stat, val in self.tvs.items() if val
        )
        if tvs:
            res += 'TVs: %s\n' % tvs
        svs = ' / '.join(
            '%d %s' % (val, stat.name) for stat, val in self.svs.items() if val != 50
        )
        if svs:
            res += 'SVs: %s\n' % svs

        for move in self.moves:
            res += '- %s\n' % move

        return res


def gen_tems(inpt):
    if isinstance(inpt, str):
        inpt = inpt.split('\n')

    def try_yield_tem(next_tem):
        try:
            return TemTem.from_importable(next_tem)
        except Exception as err:
            error('Unable to parse the following lines:')
            for line in next_tem:
                error(line)
            error('Saw the following exception: %r' % err)

    next_tem = []
    for line in inpt:
        if not line.strip():
            if next_tem:
                if (tem := try_yield_tem(next_tem)):
                    yield tem
                next_tem = []
        else:
            next_tem.append(line)

    if next_tem:
        try_yield_tem(next_tem)


# Tests
def test_temtem_class():
    from test_data import (
        GYALIS_IMPORT,
        GYALIS_STATS,
        GYALIS_TEM,
        KINU_IMPORT,
        KINU_TEM,
    )

    # test stat calculation
    assert GYALIS_TEM.stats == GYALIS_STATS

    # test boost application and TemTem._calc_live_stats
    GYALIS_TEM.apply_boost(Stats.Atk, 2)
    assert GYALIS_TEM.live_stats[Stats.Atk] == 302
    GYALIS_TEM.apply_boost(Stats.Atk, 1)
    assert GYALIS_TEM.live_stats[Stats.Atk] == 377
    GYALIS_TEM.apply_boost(Stats.Def, -6)
    assert GYALIS_TEM.boosts[Stats.Def] == -5
    assert GYALIS_TEM.live_stats[Stats.Def] == 23
    GYALIS_TEM.clear_boosts()
    assert GYALIS_TEM.live_stats == GYALIS_STATS

    # TODO: test clear_boosts, apply_boost, apply_status, end_turn, take_damage

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
    from test_data import MULTI_IMPORT, GYALIS_TEM, KINU_TEM

    with open(SAMPLE_SETS, 'r') as fp:
        next(gen_tems(fp))

    gen = gen_tems(MULTI_IMPORT)
    assert next(gen) == GYALIS_TEM
    assert next(gen) == KINU_TEM
