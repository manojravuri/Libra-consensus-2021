# from .Safety import Safety
# from .BlockTree import BlockTree
# from .BlockTree import TimeoutMsg

from Safety import Safety
from BlockTree import BlockTree
from BlockTree import TimeoutMsg,TC
import threading


class PaceMaker:
    def __init__(self, safety, block_tree, current_round=0, last_round_tc=None, pending_timeouts=None, ps = None):

        self.current_round = current_round
        self.last_round_tc = last_round_tc
        self.pending_timeouts = {}
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
        # self.timer = threading.Timer(self.get_round_timer(new_round), self.local_timeout_round)
        # self.timer.start()
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
        return time_out_msg
        #c = logical_clock()
        #send(('time_out_msg',time_out_msg,c),to=ps)

    def process_remote_timeout(self, tmo):
        tmo_info = tmo.tmo_info
        if tmo_info:
            if (tmo_info.round < self.current_round):
                return None
            if(tmo_info.round not in self.pending_timeouts):
                self.pending_timeouts[tmo_info.round]={}
                self.pending_timeouts[tmo_info.round]["tmos"]=[]
                self.pending_timeouts[tmo_info.round]["senders"]=[]
            if ( tmo_info.sender not in self.pending_timeouts[tmo_info.round]["senders"]):
                self.pending_timeouts[tmo_info.round]["tmos"].append(tmo_info)
                self.pending_timeouts[tmo_info.round]["senders"].append(tmo_info.sender)
            if (len(self.pending_timeouts[tmo_info.round]["senders"]) ==  2):
                self.stop_timer(self.current_round)
                self.local_timeout_round()
            if (len(self.pending_timeouts[tmo_info.round]["senders"]) ==  2):
                round = tmo_info.round
                tmo_high_qc_rounds = []
                signatures=[]
                for tmo_info_in_round in self.pending_timeouts[tmo_info.round]["tmos"]:
                    tmo_high_qc_rounds.append(tmo_info_in_round.round)
                    signatures.append(tmo_info_in_round.signature)
                return TC(round = round, tmo_high_qc_rounds=tmo_high_qc_rounds, tmo_signatures=signatures)
        return None

    def advance_round_tc(self, tc):
        if (tc is None or tc.round < self.current_round):
            return False
        self.last_round_tc = tc
        self.stop_timer(self.current_round)
        self.start_timer(tc.round + 1)
        return True

    def advance_round_qc(self, qc):
        # import pdb; pdb.set_trace()
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.stop_timer(self.current_round)
        self.start_timer(qc.vote_info.round + 1)
        return True
