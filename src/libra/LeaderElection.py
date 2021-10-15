import random

from Ledger import Ledger
from PaceMaker import PaceMaker
from Objects import *
import random
random.seed(10)

class LeaderElection:
    def __init__(self, ledger, pacemaker, ps, window_size=1, exclude_size=1, reputation_leaders={}):
        self.ps = list(ps)
        self.window_size = window_size
        self.exclude_size = exclude_size  # f to 2f
        self.reputation_leaders = reputation_leaders
        self.ledger = ledger
        self.pacemaker = pacemaker
        # random.seed(10)

    def elect_reputation_leader(self, qc):
        # import pdb; pdb.set_trace()
        active_validators = set()
        last_authors = set()
        current_qc = qc
        i = 0
        while i < self.window_size:# or len(last_authors) < self.exclude_size:
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            # if not current_block:
            #     return self.ps[random.randint(0, len(self.ps) - 1)]
            block_author = current_block.author if current_block else None
            signers=set()
            # import pdb; pdb.set_trace()
            if current_qc.signatures:
                for signature in current_qc.signatures:
                    signers.add(self.ps[signature.id])
            else:
                signers = signers.union(self.ps)
            if i < self.window_size:
                active_validators.update(signers)
            if len(last_authors) < self.exclude_size and block_author is not None:
                last_authors.add(block_author)
            if current_block:
                current_qc = current_block.qc
            i += 1
        active_validators = active_validators.difference(last_authors)
        # print("active_validators is ", active_validators)
        rand_index = random.randint(0, len(active_validators) - 1)
        # import pdb; pdb.set_trace()
        print("leader index in ", self.ledger.node_id , " is ", rand_index)
        return list(active_validators)[rand_index]

    def update_leader(self, qc):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = self.pacemaker.current_round
        if extended_round + 1 == qc_round and qc_round + 1 == current_round:
            # import pdb; pdb.set_trace()
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def get_leader(self, round):
        #print("round",round)
        # import pdb; pdb.set_trace()
        if self.reputation_leaders and round in self.reputation_leaders:
            return self.reputation_leaders[round]
        return self.ps[int((round / 2) % len(self.ps))]
        # return self.ps[int((round) % len(self.ps))]
