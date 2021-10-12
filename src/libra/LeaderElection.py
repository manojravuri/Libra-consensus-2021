import random

from .Ledger import Ledger
from .PaceMaker import PaceMaker


class LeaderElection:
    def __init__(self,ledger, pacemaker, nodes=None, window_size=3, exclude_size=None, reputation_of_leaders={}):
        self.nodes = nodes
        self.window_size = window_size
        self.exclude_size = exclude_size
        self.reputation_of_leaders = reputation_of_leaders
        self.ledger = ledger
        self.pacemaker = pacemaker

    def elect_reputation_leader(self, qc):
        active_nodes = []
        last_authors = set()
        current_qc = qc
        print("in erl")
        i = 0
        while (i<self.window_size or len(last_authors) < self.exclude_size):
        # for i in range(self.window_size):
            # if (len(last_authors) < self.exclude_size):
            print("parent id is ", current_qc.vote_info.parent_id)
            print(self.ledger.current_ledger)
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            if current_block:
                block_author = current_block.author
                if (i < self.window_size):
                    active_nodes.append(current_qc.signatures.signers())

                if (len(last_authors) < self.exclude_size):
                    last_authors.add(block_author)
                current_qc = current_block.qc
                i += 1
            else:
                active_nodes=self.nodes
                break
        print("active_nodes is ", active_nodes)
        #active_nodes=active_nodes-last_authors
        #check random seed
        random.seed(qc.vote_info.round)
        return active_nodes[random.randint(0,len(active_nodes)-1)]

    def update_leader(self, qc):
        if (qc and qc.vote_info):
            extended_round = qc.vote_info.parent_round
            qc_round = qc.vote_info.round
            current_round = self.pacemaker.current_round
            print("in here")
            if (extended_round + 1 == qc_round and qc_round + 1 == current_round):
                self.reputation_of_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def get_leader(self, round):
        if (self.reputation_of_leaders and  round in self.reputation_of_leaders):
            return self.reputation_of_leaders[round]
        # idx=(((round+2)/2)%len(self.nodes))
        # return idx,self.nodes[(((round+2) / 2) % len(self.nodes))]
        idx=(((round)/2)%len(self.nodes))
        return idx,self.nodes[(((round) / 2) % len(self.nodes))]
