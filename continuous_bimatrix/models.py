# -*- coding: utf-8 -*-
# <standard imports>
from __future__ import division
from otree.db import models
from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Decision

from otree import widgets
from otree.common import Currency as c, currency_range

import random
# </standard imports>

doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class Constants(BaseConstants):
    name_in_url = 'continuous_bimatrix'
    players_per_group = 2
    num_rounds = 1

    #  Points made if player defects and the other cooperates""",
    defect_cooperate_amount = 300

    # Points made if both players cooperate
    cooperate_amount = 200
    cooperate_defect_amount = 0
    defect_amount = 100
    base_points = 50

    # Amount of time the game stays on the decision page in seconds
    game_length = 120

    training_1_choices = [
        'Alice gets 300 points, Bob gets 0 points',
        'Alice gets 200 points, Bob gets 200 points',
        'Alice gets 0 points, Bob gets 300 points',
        'Alice gets 100 points, Bob gets 100 points'
    ]

    training_1_correct = training_1_choices[0]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    training_question_1 = models.CharField(
        choices=Constants.training_1_choices,
        widget=widgets.RadioSelect(),
        #timeout_default=Constants.training_1_choices[1]
    )

    def is_training_question_1_correct(self):
        return self.training_question_1 == Constants.training_1_correct

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        self.decisions_over_time = Decision.objects.filter(
                component='otree-bimatrix',
                session=self.session,
                subsession=self.subsession.name(),
                round=self.round_number,
                group=self.group.id_in_subsession)

        payoff = 0
        my_state = None
        other_state = None
        for i, change in enumerate(self.decisions_over_time):
            if change.participant == self.participant:
                my_state = change.decision
            else:
                other_state = change.decision

            if my_state != None and other_state != None:
                if my_state == 0:
                    if other_state == 0:
                        cur_payoff = float(Constants.cooperate_amount) / Constants.game_length
                    else:
                        cur_payoff = float(Constants.cooperate_defect_amount) / Constants.game_length
                else:
                    if other_state == 0:
                        cur_payoff = float(Constants.defect_cooperate_amount) / Constants.game_length
                    else:
                        cur_payoff = float(Constants.defect_amount) / Constants.game_length

                if i == len(self.decisions_over_time) - 1:
                    next_change_time = self.session.vars['end_time']
                else:
                    next_change_time = self.decisions_over_time[i + 1].timestamp

                payoff += (next_change_time - change.timestamp).total_seconds() * cur_payoff

        self.payoff = payoff
