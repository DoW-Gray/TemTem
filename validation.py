# vim: set fileencoding=utf-8 :
"""
validation.py: validation checks to confirm input teams and choices
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

from static import Types, lookup_attack, lookup_temtem_data

TEMTEM_CHECKS = {}
TEAM_CHECKS = {}
CHOICE_CHECKS = {}


class ValidationFailure(Exception):
    pass


def temtem_check(func):
    global TEMTEM_CHECKS
    TEMTEM_CHECKS[func.__name__] = func


def team_check(func):
    global TEAM_CHECKS
    TEAM_CHECKS[func.__name__] = func


def choice_check(func):
    global CHOICE_CHECKS
    CHOICE_CHECKS[func.__name__] = func


def check_temtem(temtem, ignore_rules=[]):
    for rule, check in TEMTEM_CHECKS.items():
        if rule not in ignore_rules:
            check(temtem)


def check_team(team, ignore_rules=[]):
    for temtem in team:
        check_temtem(temtem, ignore_rules)

    for rule, check in TEAM_CHECKS.items():
        if rule not in ignore_rules:
            check(team)


def check_choices(choices, team_idx, battle, ignore_rules=[]):
    for rule, check in CHOICE_CHECKS.items():
        if rule not in ignore_rules:
            check(choices, team_idx, battle)


@temtem_check
def tv_limits(temtem):
    for tv in temtem.tvs.values():
        if tv > 500:
            raise ValidationFailure(f'{temtem.species} has a tv of {tv} > 500.')
        if tv < 0:
            raise ValidationFailure(f'{temtem.species} has a tv of {tv} < 0.')


@temtem_check
def sv_limits(temtem):
    for sv in temtem.svs.values():
        if sv > 50:
            raise ValidationFailure(f'{temtem.species} has an sv of {sv} > 50.')
        if sv < 1:
            raise ValidationFailure(f'{temtem.species} has an sv of {sv} < 1.')


@temtem_check
def tem_moves(temtem):
    tem_data = lookup_temtem_data(temtem.species)
    all_moves = {move for learnset in tem_data['Moves'].values() for move in learnset}
    for move in temtem.moves:
        if move not in all_moves:
            raise ValidationFailure(f'{temtem.species} does not learn {move}')


@temtem_check
def move_count(temtem):
    if len(temtem.moves) > 4:
        # I think this should be `!= min(4, len(tem_data.moves['Level Up']))`
        # but I'd have to work out which moves the tem learns at that level.
        # Considering having too few moves is never an issue, I'm not bothering.
        raise ValidationFailure(f'{temtem.species} has more than 4 moves.')


@temtem_check
def tem_trait(temtem):
    tem_data = lookup_temtem_data(temtem.species)
    if temtem.trait not in tem_data['Traits']:
        raise ValidationFailure(f'{temtem.species} can\'t have trait {temtem.trait}')


@team_check
def species_clause(team):
    species = set()
    for tem in team:
        if tem.species in species:
            raise ValidationFailure(f'Can\'t have more than one {tem.species}.')
        species.add(tem.species)


@team_check
def gear_clause(team):
    all_gear = set()
    for tem in team:
        if tem.gear in all_gear:
            raise ValidationFailure(f'Can\'t have more than one {tem.gear}.')
        all_gear.add(tem.gear)


@team_check
def tem_count(team):
    max_tem_count = 8
    if len(team) > max_tem_count:  # TODO: check if this should be !=
        raise ValidationFailure(
            f'Team has {len(team)} tems, but the maximum is {max_tem_count}'
        )


@choice_check
def choice_actions(choices, team_idx, battle):
    for choice in choices:
        if choice.action not in ('run', 'item', 'switch', 'rest', 'attack'):
            raise ValidationFailure(f'Unknown choice action {choice.action}.')


@choice_check
def competitive_no_running(choices, team_idx, battle):
    for choice in choices:
        if choice.action == 'run':
            raise ValidationFailure('Can\'t run from a competitive battle.')


@choice_check
def competitive_no_items(choices, team_idx, battle):
    for choice in choices:
        if choice.action == 'item':
            raise ValidationFailure(
                'Can\'t use items from the bag in a competitive battle.'
            )


@choice_check
def switch_fainted(choices, team_idx, battle):
    for tem_no, choice in enumerate(choices):
        if choice.action != 'switch':
            continue
        target = battle.active_tem(team_idx, choice.target)
        if target.fainted:
            raise ValidationFailure(
                f'{battle.active_tem(team_idx, tem_no).species} is attempting '
                f'to switch to {target.species}, which is fainted.'
            )


@choice_check
def switch_already_out(choices, team_idx, battle):
    for choice in choices:
        if choice.action == 'switch' and choice.target in battle.active[team_idx]:
            raise ValidationFailure(
                'Attempting to switch to '
                f'{battle.active_tem(team_idx, choice.target).species}, which '
                'is already out.'
            )


@choice_check
def switch_same_slot(choices, team_idx, battle):
    targets = set()
    for choice in choices:
        if choice.action != 'switch':
            continue
        target = battle.active_tem(team_idx, choice.target)
        if target in targets:
            raise ValidationFailure(
                'Multiple tems are trying to switch to the same slot.'
            )
        targets.add(target)


@choice_check
def switch_already_trapped(choices, team_idx, battle):
    # TODO: check this is actually the case - it might just fail instead?
    for choice, tem_no in enumerate(choices):
        if choice.action == 'switch':
            this_tem = battle.active_tem(team_idx, tem_no)
            if this_tem.trapped:
                raise ValidationFailure(
                    f'Tem {this_tem.species} can\'t try to switch when it\'s '
                    'trapped at the start of the turn.'
                )


@choice_check
def overexerted_attack(choices, team_idx, battle):
    for choice, tem_no in enumerate(choices):
        if choice.action != 'attack':
            continue
        this_tem = battle.active_tem(team_idx, tem_no)
        if this_tem.overexerted:
            raise ValidationFailure(
                f'Tem {this_tem.species} is overexerted, but trying to attack.'
            )


@choice_check
def has_attack(choices, team_idx, battle):
    for choice, tem_no in enumerate(choices):
        if choice.action != 'attack':
            continue
        this_tem = battle.active_tem(team_idx, tem_no)
        if choice.detail.split(' +')[0] not in this_tem.moves:
            raise ValidationFailure(
                f'Tem {this_tem.species} doesn\'t have move {choice.detail}'
            )


@choice_check
def correct_synergy(choices, team_idx, battle):
    for choice, tem_no in enumerate(choices):
        if choice.action != 'attack':
            continue
        this_tem = battle.active_tem(team_idx, tem_no)
        atk = lookup_attack(choice.detail)
        if 'synergy attack' in atk:
            synergy_type = atk['name'].split(' +')[1]
            if Types[synergy_type] not in this_tem.ally.types:
                raise ValidationFailure(
                    f'Can\'t use synergy move {choice.detail} because ally '
                    f'{this_tem.ally.species} doesn\'t have type {synergy_type}'
                )
        elif 'synergy type' in atk:
            if atk['synergy type'] in this_tem.ally.types:
                raise ValidationFailure(
                    f'Tem {this_tem.species} should choose synergy move '
                    f'{atk["name"] + " +" + atk["synergy type"].name} because '
                    f'of its ally {this_tem.ally.species}\'s typing.'
                )


@choice_check
def valid_attack_target(choices, team_idx, battle):
    for tem_idx, choice in enumerate(choices):
        if choice.action != 'attack':
            continue
        atk = choice.detail
        if isinstance(atk, str):
            atk = lookup_attack(choice.detail)
        targetting = atk['target']

        if 'synergy move' in atk:
            # The following was checked by using Awful Song with a neutral tem
            # partner.
            raise ValidationFailure(
                f'Saw move {atk["name"]}, but expect targetting to be chosen '
                'based on non-synergy versions of moves.'
            )

        num_targets = len(choice.targets)
        if not num_targets:
            raise ValidationFailure(f'{choice.detail} had no targets.')

        if len({tuple(tar) for tar in choice.targets}) != num_targets:
            raise ValidationFailure(
                f'{choice.detail} targetted the same tem twice.'
            )

        if targetting in ('single', 'clockwise', 'other'):
            # For clockwise, only specify the first target
            if num_targets != 1:
                raise ValidationFailure(
                    f'Expected one target for {choice.detail}, but saw '
                    f'{num_targets}.'
                )
            if targetting == 'other' and choice.targets == [team_idx, tem_idx]:
                raise ValidationFailure(
                    f'Attack {choice.detail} can\'t target the tem using it.'
                )

        elif targetting == 'self':
            if choice.targets != [team_idx, tem_idx]:
                raise ValidationFailure(
                    f'Move {choice.detail} must target the tem using it.'
                )

        elif targetting == 'team or ally':
            if len({side for side, tem in choice.targets}) > 1:
                raise ValidationFailure(
                    f'All targets of {choice.detail} must be on the same team.'
                )
            if choice.targets[0][0] == team_idx:
                if num_targets > 1:
                    raise ValidationFailure(
                        f'Can\'t target both yourself and your ally with move '
                        f'{choice.detail}'
                    )
            elif num_targets != len(battle.active[not team_idx]):
                raise ValidationFailure(
                    f'If targetting the opposing side with {choice.detail}, '
                    'must target all opposing tems.'
                )

        elif targetting == 'whole team':
            if len({side for side, tem in choice.targets}) > 1:
                raise ValidationFailure(
                    f'All targets of {choice.detail} must be on the same team.'
                )
            if len(battle.active[choice.targets[0][0]]) != num_targets:
                raise ValidationFailure(
                    f'{choice.detail} must target all tems on a team.'
                )

        elif targetting == 'all':
            if sum((len(battle.active[i]) for i in (0, 1))) != num_targets:
                raise ValidationFailure(
                    f'{choice.detail} must target all tems on the field.'
                )

        else:
            raise RuntimeError(
                f'Unknown target {targetting} for move {choice.detail}'
            )
