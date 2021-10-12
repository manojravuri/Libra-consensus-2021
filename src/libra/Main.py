from .BlockTree import BlockTree
from .LeaderElection import LeaderElection
from .PaceMaker import PaceMaker
from .Safety import Safety
from .MemPool import MemPool
from .Ledger import Ledger
from .BlockTree import ProposalMsg

import pickle


class Message:
    def __init__(self, type=None, block=None, high_commit_qc=None, last_round_tc=None, tmo_info=None):
        self.type = type
        self.block = block
        self.high_commit_qc = high_commit_qc
        self.last_round_tc = last_round_tc
        self.tmo_info = tmo_info


class Proposal(Message):
    def __init__(self):
        pass


class Main:
    def __init__(self, id=None, nodes=None):
        self.id = id
        self.mempool = MemPool()
        self.ledger = Ledger(id,self.mempool)
        self.safety = Safety(self.ledger)
        self.block_tree = BlockTree(self.ledger)
        self.pacemaker = PaceMaker(self.safety,self.block_tree,current_round=0)
        self.leader_election = LeaderElection(self.ledger,pacemaker=self.pacemaker, nodes=nodes)

    def sync(self, round_number):
        self.pacemaker.current_round = round_number


    def current_leader(self):
        if (id == self.leader_election.get_leader()):
            return True
        else:
            return False

    def can_send(self):
        if(self.leader_election.get_leader(self.pacemaker.current_round)[0]==self.id):
            return True
        else:
            return False


    def start_event_processing(self,M,type):
        # print("M in sep is, ", M)
        message=pickle.loads(M)
        if(type=='local_timeout'):
            self.pacemaker.local_timeout_round()
        if(type=='proposal_message'):
            msg = self.process_proposal_msg(message)
            if msg:
                return msg
        if(type == 'vote_message'):
            msg = self.process_vote_msg(message)
            print("got msg in sep , " ,msg)
            if msg:
                return msg
            else:
                return None, None
        if(type == 'timeout_mesaage'):
            self.process_timeout_message(message)

    def process_certificate_qc(self, qc):
        self.block_tree.process_qc(qc)
        print("process qc done")
        self.leader_election.update_leader(qc)
        print("leader election done")
        self.pacemaker.advance_round_qc(qc)
        print("advance round done")

    def process_proposal_msg(self, P):
        print("Processing proposal message")
        print("processing certificate qc")
        self.process_certificate_qc(P.block.qc)
        print("processing high commit qc")
        self.process_certificate_qc(P.high_commit_qc)
        print("Advancing current round")
        self.pacemaker.advance_round_tc(P.last_round_tc)
        print("advanced round")
        round = self.pacemaker.current_round
        leader = self.leader_election.get_leader(round)
        if (P.block.round != round or P.sender != leader or P.block.author != leader):
            return
        print("generating block")
        block_P = self.block_tree.generate_block(self.id,self.mempool.get_transactions()[0],round,P.high_commit_qc)
        print("generated block")
        self.block_tree.execute_and_insert(block_P)
        print("executed and inserted")
        vote_msg=self.safety.make_vote(block_P, P.last_round_tc, P.high_commit_qc)
        vote_msg.ledger_commit_info.vote_info_hash.round=round+1
        print("make vote done")
        if(vote_msg is not None):
            vote_msg.author = self.id
            vote_msg.author_signature = self.id
            vote_msg.block = block_P
            print("new leader is, ", self.leader_election.get_leader(round+1))
            return pickle.dumps(vote_msg),(self.leader_election.get_leader(round+1))
            #send vote_msg to LeaderElection.get_leader(current_round+1)

    def process_timeout_message(self, M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc = self.pacemaker.process_remote_timeout(M)
        if (tc ):
            self.pacemaker.advance_round_tc(tc)
            self.process_new_round_event(tc)

    def process_new_round_event(self, last_tc=None):
        # u = self.id
        u = self.leader_election.get_leader(self.pacemaker.current_round)
        # if u == self.leader_election.get_leader(self.pacemaker.current_round):
        b = self.block_tree.generate_block(u, self.mempool.get_transactions(), self.pacemaker.current_round,
                                           high_qc=self.block_tree.high_commit_qc)
        p = ProposalMsg(b, last_tc, self.block_tree.high_commit_qc,
                        self.safety.valid_signatures(high_qc=self.block_tree.high_commit_qc, last_tc=last_tc), last_tc, u)
        return pickle.dumps(p)
        # return None

    def process_vote_msg(self, M):
        print("Mis ", M)
        qc = self.block_tree.process_vote(M)
        print("qc done")
        print("qc",qc)
        if (qc):
            self.process_certificate_qc(qc)
            print("here is it")
            return self.process_new_round_event(qc.last_tc), self.leader_election.get_leader(self.pacemaker.current_round)
            #return None, self.leader_election.get_leader(self.pacemaker.current_round)

    def workload_exists(self):
        if(self.mempool.get_transactions()):
            return True
        else:
            return False
