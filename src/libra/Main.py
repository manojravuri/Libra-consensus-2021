from BlockTree import BlockTree
from LeaderElection import LeaderElection
from PaceMaker import PaceMaker
from Safety import Safety
from MemPool import MemPool
from Ledger import Ledger
from Objects import *

import pickle



class Main:
    def __init__(self, id, curr_pr, ps=None):

        self.id = id
        self.mempool = MemPool()
        self.win_sz = 1
        self.ledger = Ledger(id, self.mempool, self.win_sz)
        self.safety = Safety(self.ledger)
        self.block_tree = BlockTree(self.ledger,f=int(len(ps)/3))
        self.pacemaker = PaceMaker(self.safety, self.block_tree, current_round=0)
        self.curr_pr = curr_pr
        ps.append(curr_pr)
        self.leader_election = LeaderElection(self.ledger, window_size=self.win_sz, pacemaker=self.pacemaker, ps=ps)

    def sync(self, round_number):
        self.pacemaker.current_round = round_number

    def current_leader(self):
        return id == self.leader_election.get_leader()

    def can_send(self):
        return self.leader_election.get_leader(self.pacemaker.current_round) == self.curr_pr

    def start_event_processing(self, message, type):
        if (type == 'local_timeout'):
            self.pacemaker.local_timeout_round()
        if (type == 'proposal_message'):
            msg = self.process_proposal_msg(message)
            if msg:
                return msg
        if (type == 'vote_message'):
            msg = self.process_vote_msg(message)
            print("got msg in sep , ", msg)
            if msg:
                return msg
            else:
                return None, None
        if (type == 'timeout_mesaage'):
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
        #block_P = self.block_tree.generate_block(self.id, self.mempool.get_transactions()[0], round, P.high_commit_qc)
        print("generated block")
        self.block_tree.execute_and_insert(P)
        print("executed and inserted")
        vote_msg = self.safety.make_vote(P.block, P.last_round_tc, P.high_commit_qc)
        print("make vote done")
        if (vote_msg is not None):
            vote_msg.author = self.id
            vote_msg.author_signature = self.id
            print("new leader is, ", self.leader_election.get_leader(round + 1))
            return vote_msg, (self.leader_election.get_leader(round + 1))
            # send vote_msg to LeaderElection.get_leader(current_round+1)

    def process_timeout_message(self, M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc = self.pacemaker.process_remote_timeout(M)
        if (tc):
            self.pacemaker.advance_round_tc(tc)
            self.process_new_round_event(tc)

    def process_new_round_event(self, last_tc=None):
        u = self.leader_election.get_leader(self.pacemaker.current_round)
        # if u == self.leader_election.get_leader(self.pacemaker.current_round):
        b = self.block_tree.generate_block(u, self.mempool.get_transactions(), self.pacemaker.current_round)
        p = ProposalMsg(b, last_tc, self.block_tree.high_commit_qc,u)
        return p
        # return None

    def process_vote_msg(self, M):
        print("Mis ", M)
        qc = self.block_tree.process_vote(M)
        print("qc done")
        if (qc):
            self.process_certificate_qc(qc)
            print("here is it")
            return self.process_new_round_event(None), self.leader_election.get_leader(self.pacemaker.current_round)
            # return None, self.leader_election.get_leader(self.pacemaker.current_round)

    def workload_exists(self):
        if (self.mempool.get_transactions()):
            return True
        else:
            return False

    def add_to_Mempool(self, M):
        self.mempool.add_to_queue(M)


class Replica1():
    def __init__(self,id):
        self.id=id

if __name__ == '__main__':

    nodes=[]
    for i in range(10):
        nodes.append(Replica1(i))
    main1 = Main(0,nodes[0],nodes)
    main2=Main(1,nodes[1],nodes)
    main3 = Main(2,nodes[2], nodes)
    main4 = Main(3, nodes[1], nodes)
    main5 = Main(4, nodes[2], nodes)
    p1=main1.process_new_round_event()
    print(p1)
    vote_msg_2,leader_2 =main2.start_event_processing(p1,'proposal_message')
    vote_msg_3, leader_3 = main3.start_event_processing(p1, 'proposal_message')
    vote_msg_4, leader_4 = main4.start_event_processing(p1, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(p1, 'proposal_message')
    # import pdb; pdb.set_trace()
    proposal_msg_2, leader_2 = main2.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_5, 'vote_message')

    vote_msg_2, leader_2 = main1.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_3, leader_3 = main3.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_4, leader_4 = main4.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(proposal_msg_2, 'proposal_message')

    proposal_msg_2, leader_2 = main3.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg, leader = main3.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main3.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main3.start_event_processing(vote_msg_5, 'vote_message')

    # proposal_msg,leader=main2.start_event_processing(vote_msg,'vote_message')
    # # pdb.set_trace()
    # vote_msg,leader=main3.start_event_processing(proposal_msg,'proposal_message')
    # # pdb.set_trace()
    # proposal_msg, leader = main4.start_event_processing(vote_msg, 'vote_message')
    # # pdb.set_trace()
    # vote_msg, leader = main5.start_event_processing(proposal_msg, 'proposal_message')