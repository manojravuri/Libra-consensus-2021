import libra.Safety as Safety
from libra.Safety import Safety
import libra.BlockTree as BlockTree
from libra.BlockTree import BlockTree
from libra.BlockTree import TimeoutMsg


class PaceMaker:
    def __init__(self, safety, block_tree, current_round=0, last_round_tc=None, pending_timeouts=None):

        self.current_round = current_round
        self.last_round_tc = last_round_tc
        self.pending_timeouts = pending_timeouts
        self.safety = safety
        self.block_tree = block_tree

    def stop_timer(self, round):
        pass

    def get_round_timer(self, r):
        # c=logical_clock()
        return None

    def start_timer(self, new_round):
        self.stop_timer(self.current_round)
        self.current_round = new_round
        return self.get_round_timer(self, self.current_round)

    def local_timeout_round(self):
        # save_consensus_state()
        timeout_info = self.safety.make_timeout(self.current_round, self.block_tree.high_qc, self.last_round_tc)
        # broadcast TimeoutMsg(timeout_info,self.last_round_tc,self.block_tree.high_commit_qc)

    def process_remote_timeout(self, tmo):
        tmo_info = tmo.tmo_info
        if (tmo_info.round < self.current_round):
            return None
        if (tmo_info.sender not in self.pending_timeouts):
            self.pending_timeouts.add(tmo_info)
        if (self.pending_timeouts.size() == f + 1):
            self.stop_timer(self.current_round)
            self.local_timeout_round()
        if (self.pending_timeouts.size() == 2 * f + 1):
            round = tmo_info.round
            tmo_high_qc_rounds = self.pending_timeouts[tmo_info.round][0].high_qc.round
            signatures = self.pending_timeouts[tmo_info.round][0].signature
        return None

    def advance_round_tc(self, tc):
        if (tc is None or tc.round < self.current_round):
            return False
        self.last_round_tc = tc
        self.start_timer(tc.round + 1)
        return True

    def advance_round_qc(self, qc):
        if (qc.vote_info.round < self.current_round):
            return False
        self.last_round_tc = None
        self.start_timer(qc.vote_info.round + 1)
        return True
