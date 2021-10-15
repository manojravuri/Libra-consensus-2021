from BlockTree import BlockTree
from LeaderElection import LeaderElection
from PaceMaker import PaceMaker
from Safety import Safety
from MemPool import MemPool
from Ledger import Ledger
from Objects import *
import copy

from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

import pickle



class Main:
    def __init__(self, id, curr_pr, ps=None, all_replica_public_keys=None,all_client_public_keys=None,replica_private_key=None):
        self.id = id
        self.mempool = MemPool()
        self.win_sz = 1
        self.ledger = Ledger(id, self.mempool, self.win_sz)
        self.safety = Safety(id,self.ledger,highest_vote_round=-1,highest_qc_round=-1,private_key=replica_private_key,replica_public_keys=all_replica_public_keys,client_public_keys=all_client_public_keys, curr_pr = curr_pr)
        self.block_tree = BlockTree(self.ledger,self.safety,f=int(len(ps)/3))
        self.pacemaker = PaceMaker(self.safety, self.block_tree, current_round=0, ps = ps)
        self.curr_pr = curr_pr
        self.leader_election = LeaderElection(self.ledger, window_size=self.win_sz, pacemaker=self.pacemaker, ps=ps)

    def sync(self, round_number):
        self.pacemaker.current_round = round_number

    def current_leader(self):
        return id == self.leader_election.get_leader()

    def can_send(self):
        print("can_send is, ", self.leader_election.get_leader(self.pacemaker.current_round) == self.id)
        print(self.pacemaker.current_round , self.id)
        return self.leader_election.get_leader(self.pacemaker.current_round) == self.curr_pr
        # return self.leader_election.get_leader(self.pacemaker.current_round) == self.id

    def start_event_processing(self, message, type):
        # print("M is, ", M)
        # message = pickle.loads(M)
        # print("message is, ", message)
        if (type == 'local_timeout'):
            msg = self.pacemaker.local_timeout_round()
        if (type == 'proposal_message'):

            msg = self.process_proposal_msg(message)

            if msg:
                return msg
                # return pickle.dumps(msg[0]), msg[1]
        if (type == 'vote_message'):
            msg = self.process_vote_msg(message)
            #print("got msg in sep , ", msg)
            if msg:
                return msg
                # return pickle.dumps(msg[0]), msg[1]
            else:
                return None, None
        if (type == 'timeout_message'):
            msg = self.process_timeout_message(message)
            if msg:
                return msg
                # return pickle.dumps(msg[0]), msg[1]
            else:
                return None, None
    def process_certificate_qc(self, qc):
        self.block_tree.process_qc(qc)
        #print("process qc done")
        self.leader_election.update_leader(qc)
        #print("leader election done")
        self.pacemaker.advance_round_qc(qc)
        #print("advance round done")

    def process_proposal_msg(self, P):
        #print("Processing proposal message")
        #print("processing certificate qc")
        # print("P is, ", P)
        # print("P.block.qc")
        self.process_certificate_qc(P.block.qc)
        # print("P.block.qc done")
        #print("processing high commit qc")
        self.process_certificate_qc(P.high_commit_qc)
        #print("Advancing current round")
        self.pacemaker.advance_round_tc(P.last_round_tc)
        #print("advanced round")
        self.mempool.get_transactions() ## TODO: have to remove transaction from mempool
        round = self.pacemaker.current_round
        leader = self.leader_election.get_leader(round)
        if (P.block.round != round or P.sender != leader or P.block.author != leader):
            return
        #print("generating block")
        #block_P = self.block_tree.generate_block(self.id, self.mempool.get_transactions()[0], round, P.high_commit_qc)
        #print("generated block")
        self.block_tree.execute_and_insert(P)
        #print("executed and inserted")
        vote_msg = self.safety.make_vote(P.block, P.last_round_tc, P.high_commit_qc)
        #print("make vote done")
        if (vote_msg is not None):
            return vote_msg, (self.leader_election.get_leader(round + 1))
            # send vote_msg to LeaderElection.get_leader(current_round+1)

    def process_timeout_message(self, M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc = self.pacemaker.process_remote_timeout(M)
        if (tc):
            self.pacemaker.advance_round_tc(tc)
            return self.process_new_round_event(tc), self.leader_election.get_leader(self.pacemaker.current_round)

    def process_new_round_event(self, last_tc=None):
        # import pdb; pdb.set_trace()
        u = self.leader_election.get_leader(self.pacemaker.current_round)
        if self.curr_pr == u:
            b = self.block_tree.generate_block(u, self.mempool.get_transactions(), self.pacemaker.current_round)
            p = ProposalMsg(b, last_tc, self.block_tree.high_commit_qc, u)
        # return pickle.dumps(p), self.leader_election.get_leader(self.pacemaker.current_round)
            return p
        # return None

    def process_vote_msg(self, M):
        #print("Mis ", M)
        qc = self.block_tree.process_vote(M)
        #print("qc done")
        if (qc):
            self.process_certificate_qc(qc)
            #print("here is it")
            # import pdb; pdb.set_trace()
            qc.author = self.curr_pr
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

    def __repr__(self):
        return "author is " + str(self.id)

if __name__ == '__main__':

    nodes=[]

    all_replica_public_keys = []
    all_replica_private_keys = []

    for i in range(5):
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        verify_key_b64 = verify_key.encode(encoder=HexEncoder)
        all_replica_public_keys.append(verify_key_b64)
        all_replica_private_keys.append(signing_key)

    ##clients

    #cps = new(Client, num=number_of_clients)

    all_client_private_keys = []
    all_client_public_keys = []

    for i in range(number_of_clients):
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        verify_key_b64 = verify_key.encode(encoder=HexEncoder)
        all_client_public_keys.append(verify_key_b64)
        all_client_private_keys.append(signing_key)

    for i in range(10):
        nodes.append(Replica1(i))
    main1 = Main(0,nodes[0],nodes,all_replica_public_keys=all_replica_public_keys,all_client_public_keys=all_client_public_keys,replica_private_key=all_replica_private_keys[0])
    main2=Main(1,nodes[1],nodes,all_replica_public_keys=all_replica_public_keys,all_client_public_keys=all_client_public_keys,replica_private_key=all_replica_private_keys[1])
    main3 = Main(2,nodes[2], nodes,all_replica_public_keys=all_replica_public_keys,all_client_public_keys=all_client_public_keys,replica_private_key=all_replica_private_keys[2])
    main4 = Main(3, nodes[3], nodes,all_replica_public_keys=all_replica_public_keys,all_client_public_keys=all_client_public_keys,replica_private_key=all_replica_private_keys[3])
    main5 = Main(4, nodes[4], nodes,all_replica_public_keys=all_replica_public_keys,all_client_public_keys=all_client_public_keys,replica_private_key=all_replica_private_keys[4])
    p1=main1.process_new_round_event()
    print(p1)
    # import pdb; pdb.set_trace()
    vote_msg_2,leader_2 =main2.start_event_processing(p1,'proposal_message')
    vote_msg_6, leader_6 = main1.start_event_processing(p1, 'proposal_message')
    vote_msg_3, leader_3 = main3.start_event_processing(p1, 'proposal_message')
    vote_msg_4, leader_4 = main4.start_event_processing(p1, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(p1, 'proposal_message')
    # import pdb; pdb.set_trace()
    proposal_msg_6, leader_2 = main2.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg_2, leader_6 = main2.start_event_processing(vote_msg_6, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main2.start_event_processing(vote_msg_5, 'vote_message')
    # import pdb; pdb.set_trace()
    vote_msg_2, leader_2 = main1.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_3, leader_3 = main3.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_4, leader_4 = main4.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_6, leader_6 = main2.start_event_processing(proposal_msg_2, 'proposal_message')
    # import pdb; pdb.set_trace()
    proposal_msg, leader_2 = main3.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg_2, leader = main3.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main3.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main3.start_event_processing(vote_msg_5, 'vote_message')
    proposal_msg_6, leader_6 = main3.start_event_processing(vote_msg_6, 'vote_message')
    # import pdb; pdb.set_trace()
    vote_msg_2, leader_2 = main2.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_6, leader_2 = main3.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_4, leader_4 = main4.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_3, leader_3 = main1.start_event_processing(proposal_msg_2, 'proposal_message')

    # import pdb; pdb.set_trace()
    proposal_msg_6, leader_2 = main4.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg_2, leader_2 = main4.start_event_processing(vote_msg_6, 'vote_message')
    proposal_msg, leader = main4.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main4.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main4.start_event_processing(vote_msg_5, 'vote_message')
    # import pdb; pdb.set_trace()
    vote_msg_2, leader_2 = main1.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_6, leader_2 = main4.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_3, leader_3 = main3.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_4, leader_4 = main2.start_event_processing(proposal_msg_2, 'proposal_message')
    vote_msg_5, leader_5 = main5.start_event_processing(proposal_msg_2, 'proposal_message')
    # import pdb; pdb.set_trace()
    proposal_msg_2, leader_2 = main5.start_event_processing(vote_msg_2, 'vote_message')
    proposal_msg, leader_2 = main5.start_event_processing(vote_msg_6, 'vote_message')
    proposal_msg, leader = main5.start_event_processing(vote_msg_3, 'vote_message')
    proposal_msg, leader = main5.start_event_processing(vote_msg_4, 'vote_message')
    proposal_msg, leader = main5.start_event_processing(vote_msg_5, 'vote_message')
