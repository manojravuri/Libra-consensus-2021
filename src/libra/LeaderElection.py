import random

import Ledger,PaceMaker

class LeaderElection:
    def __init__(self,validators,window_size,exclude_size,reputation_of_leaders:map):
        self.validators=validators
        self.window_size=window_size
        self.exclude_size=exclude_size
        self.reputation_of_leaders=reputation_of_leaders
        self.ledger=Ledger()
        self.pacemaker=PaceMaker

    def elect_reputation_leader(self,qc):
        active_validators=None
        last_authors=None
        current_qc=qc
        for i in range(self.window_size):
            if(last_authors.size()<self.exclude_size):
                break
            current_block=self.ledger.committed_block(current_qc.vote_info.parent_id)
            block_author=current_block.author
            if(i<self.window_size):
                active_validators.add(current_qc.signatures.signers())

            if(last_authors.size()<self.exclude_size):
                last_authors.add(block_author)
            current_qc=current_block.qc
        return active_validators.get(random.seed)

    def update_leader(self,qc):
        extended_round=qc.vote_info.parent_round
        qc_round=qc.vote_info.round
        current_round=self.pacemaker.current_round
        if(extended_round+1== qc_round and qc_round+1==current_round):
            self.reputation_of_leaders[current_round+1]=self.elect_reputation_leader(qc)


    def get_leader(self,round):
        if(round in self.reputation_of_leaders):
            return self.reputation_of_leaders[round]
        return self.validators[((round/2)%(self.validators.size()))]
