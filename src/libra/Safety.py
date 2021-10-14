from Ledger import Ledger
from Objects import *


class Safety:
    def __init__(self, ledger, private_key=None, highest_vote_round=-1, highest_qc_round=-1):
        self.private_key = private_key
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
        self.ledger = ledger

    def increase_highest_vote_round(self, round):
        self.highest_vote_round = max(round, self.highest_vote_round)

    def update_highest_qc_round(self, qc_round):
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    def consecutive(self, block_round, round):
        return round + 1

    def safe_to_extednd(self, block_round, qc_round, tc):
        return self.consecutive(self, block_round, tc, round) and qc_round >= max(tc.tmo_high_qc_rounds)

    def safe_to_vote(self, block_round, qc_round, tc):
        if (block_round <= max(self.highest_vote_round, qc_round)):
            return False
        return self.consecutive(self, block_round, qc_round) and self.safe_to_extednd(self, block_round, qc_round, tc)

    def safe_to_timeout(self, round, qc_round, tc):
        if (qc_round < self.highest_qc_round or round <= max(self.highest_vote_round - 1, qc_round)):
            return False
        return self.consecutive(self, round, qc_round) or self.consecutive(self, round, tc.round)

    def commit_state_id_candidate(self, block_round, qc,block):
        if (self.consecutive(block_round, qc.vote_info.round)):
            return self.ledger.pending_state(block.round)
        else:
            return None

    def valid_signatures(self, high_qc, last_tc):
        return True

    def make_vote(self, block, last_tc, high_commit_qc):
        # import pdb; pdb.set_trace()
        print(block)
        qc_round = block.qc.vote_info.round
        if self.valid_signatures(block, last_tc) or safe_to_vote(block.round, qc_round, last_tc):
            print(1)
            self.update_highest_qc_round(qc_round)
            print(2)
            self.increase_highest_vote_round(block.round)
            print(3)
            print(block, block.id)
            vote_info = VoteInfo(block.id, block.round, block.qc.vote_info, qc_round)
            print(4)
            ledger_commit_info = LedgerCommitInfo(self.commit_state_id_candidate(block.round, block.qc,block), vote_info)
            print(5)
            return VoteMsg(vote_info, ledger_commit_info, high_commit_qc, None, None)
        return None

    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if (self.valid_signatures(high_qc, last_tc) and self.safe_to_timeout(round, qc_round, last_tc)):
            return TimeoutInfo(round, high_qc)
        return None
