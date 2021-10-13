import random

from .Ledger import Ledger
from .PaceMaker import PaceMaker
from .Objects import *

class LeaderElection:
    def __init__(self, ledger, pacemaker, ps, window_size=1, exclude_size=None, reputation_leaders={}):
        self.ps = list(ps)
        self.window_size = window_size
        self.exclude_size = exclude_size  # f to 2f
        self.reputation_leaders = reputation_leaders
        self.ledger = ledger
        self.pacemaker = pacemaker

    def elect_reputation_leader(self, qc):
        active_validators = set()
        last_authors = set()
        current_qc = qc
        i = 0
        while i < self.window_size or len(last_authors) < self.exclude_size:
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            block_author = current_block.author
            if i < self.window_size:
                active_validators.add(current_qc.signatures.signers())
            if len(last_authors) < self.exclude_size:
                last_authors.add(block_author)
            current_qc = current_block.qc
            i += 1
        active_validators = active_validators.difference(last_authors)
        print("active_validators is ", active_validators)
        return active_validators[random.randint(0, len(active_validators) - 1)]

    def update_leader(self, qc):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = self.pacemaker.current_round
        if extended_round + 1 == qc_round and qc_round + 1 == current_round:
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def get_leader(self, round):
        print("round",round)
        if self.reputation_leaders and round in self.reputation_leaders:
            return self.reputation_leaders[round]
        return self.ps[int((round / 2) % len(self.ps))]
