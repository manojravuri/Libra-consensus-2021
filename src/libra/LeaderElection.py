import random

from libra.Ledger import Ledger
from libra.PaceMaker import PaceMaker


class LeaderElection:
    def __init__(self,ledger, pacemaker, nodes=None, window_size=None, exclude_size=None, reputation_of_leaders=None):
        self.nodes = nodes
        self.window_size = window_size
        self.exclude_size = exclude_size
        self.reputation_of_leaders = reputation_of_leaders
        self.ledger = ledger
        self.pacemaker = pacemaker

    def elect_reputation_leader(self, qc):
        active_nodes = None
        last_authors = None
        current_qc = qc
        for i in range(self.window_size):
            if (last_authors.size() < self.exclude_size):
                break
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            block_author = current_block.author
            if (i < self.window_size):
                active_nodes.add(current_qc.signatures.signers())

            if (last_authors.size() < self.exclude_size):
                last_authors.add(block_author)
            current_qc = current_block.qc
        return active_nodes.get(random.seed)

    def update_leader(self, qc):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = self.pacemaker.current_round
        if (extended_round + 1 == qc_round and qc_round + 1 == current_round):
            self.reputation_of_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def get_leader(self, round):
        if (self.reputation_of_leaders is not None and round in self.reputation_of_leaders):
            return self.reputation_of_leaders[round]
        idx=((round/2)%len(self.nodes))
        return idx,self.nodes[((round / 2) % len(self.nodes))]
