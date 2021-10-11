import libra.BlockTree as BlockTree
from libra.BlockTree import BlockTree
import libra.LeaderElection as LeaderElection
from libra.LeaderElection import LeaderElection
import libra.PaceMaker as PaceMaker
from libra.PaceMaker import PaceMaker
import libra.Safety as Safety
from libra.Safety import Safety
import libra.MemPool as MemPool
from libra.MemPool import MemPool
from libra.BlockTree import ProposalMsg

import pickle

class Message:
    def __init__(self,type = None,block = None,high_commit_qc = None,last_round_tc = None,tmo_info = None):
        self.type=type
        self.block=block
        self.high_commit_qc=high_commit_qc
        self.last_round_tc=last_round_tc
        self.tmo_info=tmo_info

class Proposal(Message):
    def __init__(self):
        pass


class Main:
    def __init__(self, id = None,nodes=None):
        self.id=id
        self.pacemaker=PaceMaker(current_round=0)
        self.block_tree=BlockTree()
        self.leader_election=LeaderElection(pacemaker=self.pacemaker,nodes=nodes)
        self.pacemaker=PaceMaker()
        self.safety=Safety()
        self.mempool=MemPool()


    def sync(self,round_number):
        self.pacemaker.current_round=round_number


    def current_leader(self):
        if(id==self.leader_election.get_leader()):
            return True
        else:
            return False

    def can_send(self):
        if(self.leader_election.get_leader(self.pacemaker.current_round)[0]==self.id):
            return True
        else:
            return False


    def start_event_processing(self,M,type):
        message=pickle.loads(M)
        if(type=='local_timeout'):
            self.pacemaker.local_timeout_round()
        if(type=='proposal_message'):
            return self.process_proposal_msg(message)
        if(type == 'vote_message'):
            return self.process_vote_msg(message)
        if(type == 'timeout_mesaage'):
            self.process_timeout_message(message)


    def process_certificate_qc(self,qc):
        self.block_tree.process_qc()
        self.leader_election.update_leader(qc)
        self.pacemaker.advance_round_qc(qc)

    def process_proposal_msg(self,P):
        self.process_certificate_qc(P.block.qc)
        self.process_certificate_qc(P.high_commit_qc)
        self.pacemaker.advance_round_tc(P.last_round_tc)
        round=self.pacemaker.current_round
        leader=self.leader_election.get_leader(round)
        if(P.block.round != round or P.sender != leader or P.block.author !=leader):
            return
        self.block_tree.execute_and_insert(P)
        vote_msg=self.safety.make_vote(P.block,P.last_round_tc)
        if(vote_msg is not None):
            return pickle.dumps(vote_msg),pickle.dumps(LeaderElection.get_leader(round+1))
            #send vote_msg to LeaderElection.get_leader(current_round+1)

    def process_timeout_message(self,M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc=self.pacemaker.process_remote_timeout(M)
        if(tc is not None):
            self.pacemaker.advance_round_tc(tc)
            self.process_new_round_event(tc)

    def process_new_round_event(self,last_tc=None):
        #print("pacemaker round",self.pacemaker.current_round)
        u= self.leader_election.get_leader(self.pacemaker.current_round)
        b=self.block_tree.generate_block(u,self.mempool.get_transactions(),self.pacemaker.current_round,high_qc=self.block_tree.high_commit_qc)
        p =ProposalMsg(b,last_tc,self.block_tree.high_commit_qc,self.safety.valid_signatures(high_qc=self.block_tree.high_commit_qc,last_tc=last_tc))
        #print("Block round for new round",p.block.round)
        return pickle.dumps(p)

    def process_vote_msg(self,M):
        qc=self.block_tree.process_vote(M)
        if(qc is not None):
            self.process_certificate_qc(qc)
            return self.process_new_round_event(qc.last_tc)
        return None

    def workload_exists(self):
        if(self.mempool.get_transactions() is not None):
            return True
        else:
            return False

