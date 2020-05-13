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

from consts import (
    Stats,
    Types,
    STAT_CONSTS,
    DEFAULT_LEVEL,
    lookup_temtem_data,
)

from logging import error, debug

class TemTem:
    def __init__(
            self,
            species,
            moves,
            trait,
            svs={},
            tvs={},
            item=None,
            level=DEFAULT_LEVEL
    ):
        self.species = species
        self.moves = moves
        self.trait = trait
        self.base_stats, self.types = lookup_temtem_data(species)
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

        self.item = item
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}
        self._calc_live_stats()

    def __repr__(self):
        return "<TemTem %s>" % self.species

    def _calc_stats(self):
        stats = {}
        for stat in Stats:
            val1 = 1.5 * self.base_stats[stat]
            debug('For stat %s, base stat = %f' % (stat.name, self.base_stats[stat]))
            val1 += self.svs[stat]
            val1 += (self.tvs[stat] / 5)
            val1 *= self.level
            val1 //= STAT_CONSTS[stat][0]
            debug('For stat %s, val1 = %f' % (stat.name, val1))
            val2 = self.svs[stat] * self.base_stats[stat] * self.level
            val2 //= STAT_CONSTS[stat][1]
            debug('For stat %s, val2 = %f' % (stat.name, val2))
            stats[stat] = int(val1 + val2 + STAT_CONSTS[stat][2])
        stats[Stats.HP] += self.level
        self.stats = stats

    def _calc_live_stats(self):
        live_stats = {}
        for stat in Stats:
            if stat in (Stats.HP, Stats.Sta):
                try:
                    live_stats[stat] = self.live_stats[stat]
                except (KeyError, AttributeError):
                    live_stats[stat] = self.stats[stat]
            elif boost := self.boosts[stat] > 0:
                live_stats[stat] = int(self.stats[stat] * (2 + boost) / 2)
            elif boost < 0:
                live_stats[stat] = max(1, 2 * self.stats[stat] / (2 + boost))
            else:
                live_stats[stat] = self.stats[stat]
        self.live_stats = live_stats

    def clear_boosts(self):
        self.boosts = {stat: 0 for stat in Stats if stat not in (Stats.HP, Stats.Sta)}
        self.live_stats = self.stats

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

        # line 1: nickname (species) @ item
        if '@' in line:
            parts = line.strip().split('@')
            item = parts[1].strip() or None
            line = parts[0]
        else:
            item = None

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

        return cls(species, moves, trait, svs, tvs, item, level)

    def export(self):
        res = '%s %s\n' % (self.species, '@ %s' % self.item if self.item else '')
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

        return res + '\n'

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
