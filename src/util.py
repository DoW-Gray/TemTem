# vim: set fileencoding=utf-8 :
"""
util.py: Various temtem-related utilities
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

from static import Stats, lookup_attack
from temtem import gen_tems


def remove_unuseful_tvs(tem):
    for stat in Stats:
        cur_stat = tem.stats[stat]
        while tem.stats[stat] == cur_stat and tem.tvs[stat] > -1:
            tem.tvs[stat] -= 1
            tem._calc_stats()
        tem.tvs[stat] += 1
        tem._calc_stats()


def try_increase_stat(tem, stat, remaining_tvs):
    cur_tvs = tem.tvs[stat]
    cur_stat = tem.stats[stat]
    last_tvs = (cur_tvs, remaining_tvs)
    while remaining_tvs and tem.tvs[stat] < 499:
        tem.tvs[stat] += 1
        remaining_tvs -= 1
        tem.stats[stat] = tem._calc_stat(stat)
        if tem.stats[stat] != cur_stat:
            cur_stat = tem.stats[stat]
            last_tvs = (tem.tvs[stat], remaining_tvs)

    tem.tvs[stat] = last_tvs[0]
    tem.stats[stat] = tem._calc_stat(stat)
    return last_tvs[1]


def try_increase_sta_regen(tem, remaining_tvs):
    from math import ceil

    def sta_regen(tem):
        return ceil(tem.stats[Stats.Sta] / 5) + 1

    cur_sta_regen = sta_regen(tem)
    cur_tvs = tem.tvs[Stats.Sta]
    last_tvs = (cur_tvs, remaining_tvs)
    while remaining_tvs and tem.tvs[Stats.Sta] < 499:
        tem.tvs[Stats.Sta] += 1
        remaining_tvs -= 1
        tem.stats[Stats.Sta] = tem._calc_stat(Stats.Sta)
        if sta_regen(tem) > cur_sta_regen:
            cur_sta_regen = sta_regen(tem)
            last_tvs = (tem.tvs[Stats.Sta], remaining_tvs)

    tem.tvs[Stats.Sta] = last_tvs[0]
    tem.stats[Stats.Sta] = tem._calc_stat(Stats.Sta)
    return last_tvs[1]


def optimise_tvs(tem):
    '''
    Try to move ineffective TVs to where they'll do more good in a tem

    We assume the following preferences:
    - Stamina if it will increase the sta regen per turn, because that's BIG
    - Speed, because going first is nice
    - Stamina, because it's very noticable when you run out
    - HP
    - Whichever atk stat is used for the strongest move
    - Def and SpD, whichever is weaker first

    You can argue that these are very arbitrary, and you'd be right.
    But I think they're generally pretty good assuming you've got most of the
    TVs where you want them already.
    '''
    remove_unuseful_tvs(tem)

    remaining_tvs = 1000 - sum(tem.tvs[stat] for stat in Stats)
    if remaining_tvs < 1:
        return

    # Next, try adding TVs where we think they will help most
    atk_stat = {'Special': 0, 'Physical': 0}
    for move in tem.moves:
        atk = lookup_attack(move)
        if (cl := atk['class']) in atk_stat:
            atk_stat[cl] = max(atk_stat[cl], atk['damage'])
    if atk_stat['Physical'] > atk_stat['Special']:
        atk_stat = Stats.Atk
    else:
        atk_stat = Stats.SpA

    if tem.stats[Stats.Def] < tem.stats[Stats.SpD]:
        def_stats = (Stats.Def, Stats.SpD)
    else:
        def_stats = (Stats.SpD, Stats.Def)

    remaining_tvs = try_increase_sta_regen(tem, remaining_tvs)
    to_increase = (Stats.Spe, Stats.Sta, Stats.HP, atk_stat, *def_stats)
    for stat in to_increase:
        if not remaining_tvs:
            break
        remaining_tvs = try_increase_stat(tem, stat, remaining_tvs)


def import_temtemstrat_sets():
    with open('sets.txt', 'r') as fp:
        return list(gen_tems(fp))
