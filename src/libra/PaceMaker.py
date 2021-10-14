# from .Safety import Safety
# from .BlockTree import BlockTree
# from .BlockTree import TimeoutMsg
from Safety import Safety
from BlockTree import BlockTree
from BlockTree import TimeoutMsg
import threading


class PaceMaker:
    def __init__(self, safety, block_tree, current_round=0, last_round_tc=None, pending_timeouts=None, ps = None):

        self.current_round = current_round
        self.last_round_tc = last_round_tc
        self.pending_timeouts = pending_timeouts
        self.safety = safety
        self.block_tree = block_tree
        self.delta = 1
        self.timer = threading.Timer(None, None)
        self.ps = ps

    def stop_timer(self, round):
        self.timer.cancel()
        pass

    def get_round_timer(self, r):
        # c=logical_clock()
        return 4 * self.delta

    def start_timer(self, new_round):
        # self.stop_timer(self.current_round)
        print("current_round is, ", new_round)
        self.current_round = new_round
        self.timer = threading.Timer(self.get_round_timer(new_round), self.local_timeout_round)
        self.timer.start()
        # return self.get_round_timer(self, self.current_round)

    def local_timeout_round(self):
        # save_consensus_state()
        print("local timeout")
        self.stop_timer(self.current_round) ## TODO: check if this is wrong or right
        print("stopped timer")
        timeout_info = self.safety.make_timeout(self.current_round, self.block_tree.high_qc, self.last_round_tc)
        print("local_timeout done")
        # broadcast TimeoutMsg(timeout_info,self.last_round_tc,self.block_tree.high_commit_qc)
        time_out_msg = TimeoutMsg(timeout_info,self.last_round_tc,self.block_tree.high_commit_qc)
        c = logical_clock()
        send(('time_out_msg_local',time_out_msg,c),to=ps)

    def process_remote_timeout(self, tmo):
        tmo_info = tmo.tmo_info
        if tmo_info:
            if (tmo_info.round < self.current_round):
                return None
            if (tmo_info.sender not in self.pending_timeouts):
                self.pending_timeouts.add(tmo_info)
            if (self.pending_timeouts.size() == f + 1):
                self.stop_timer(self.current_round)
                self.local_timeout_round()
            if (self.pending_timeouts.size() == 2 * f + 1):
                round = tmo_info.round
                tmo_high_qc_rounds = self.pending_timeouts[tmo_info.round][0].high_qc.vote_info.round
                signatures = self.pending_timeouts[tmo_info.round][0].signature
        return None

    def advance_round_tc(self, tc):
        if (tc is None or tc.round < self.current_round):
            return False
        self.last_round_tc = tc
        self.stop_timer(self.current_round)
        self.start_timer(tc.round + 1)
        return True

    def advance_round_qc(self, qc):
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.stop_timer(self.current_round)
        self.start_timer(qc.vote_info.round + 1)
        return True
