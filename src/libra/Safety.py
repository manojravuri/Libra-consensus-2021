import libra.Ledger as Ledger
from libra.Ledger import Ledger
from libra.BlockTree import VoteMsg,VoteInfo,TimeoutInfo
class Safety:
    def __init__(self,private_key = None,highest_vote_round = None,highest_qc_round = None):
        self.private_key=private_key
        self.highest_vote_round=highest_vote_round
        self.highest_qc_round=highest_qc_round
        self.ledger=Ledger()

    def increase_highest_vote_round(self,round):
        self.highest_vote_round=max(round,self.highest_vote_round)

    def update_highest_qc_round(self,qc_round):
        self.highest_qc_round=max(self.highest_qc_round,qc_round)

    def consecutive(self,block_round,round):
        return round+1

    def safe_to_extednd(self,block_round,qc_round,tc):
        return self.consecutive(self,block_round,tc,round) and qc_round>=max(tc.tmo_high_qc_rounds)

    def safe_to_vote(self,block_round,qc_round,tc):
        if(block_round<=max(self.highest_vote_round,qc_round)):
            return False
        return self.consecutive(self,block_round,qc_round) and self.safe_to_extednd(self,block_round,qc_round,tc)

    def safe_to_timeout(self,round,qc_round,tc):
        if(qc_round<self.highest_qc_round or round<=max(self.highest_vote_round-1,qc_round)):
            return False
        return self.consecutive(self,round,qc_round) or self.consecutive(self,round,tc.round)


    def commit_state_id_candidate(self,block_round,qc):
        if(self.consecutive(block_round,qc.vote_info.round)):
            return self.ledger.pending_state(self,qc.id)
        else:
            return None

    def valid_signatures(self,high_qc,last_tc):
        return True


    def make_vote(self,b,last_tc):
        return VoteMsg(VoteInfo())

    def make_timeout(self,round,high_qc,last_tc):
        qc_round=high_qc.vote_info.round
        if(self.valid_signatures(high_qc,last_tc) and self.safe_to_timeout(round,qc_round,last_tc)):
            return TimeoutInfo(round,high_qc)
        return None
