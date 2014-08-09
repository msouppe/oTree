import ptree.test
from ptree.common import Money, money_range
import matrix_asymmetric.views as views
from matrix_asymmetric.utilities import Bot
import random


class ParticipantBot(Bot):

    def play(self):

        # random decision
        choice = random.choice(['A','B'])
        self.submit(views.Decision, {"decision": choice})

        #  results
        self.submit(views.Results)

