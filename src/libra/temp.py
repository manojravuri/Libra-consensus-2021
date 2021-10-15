import os
import random
import string
import sys
import logging
import time
from collections import deque
from collections import defaultdict
from .Objects import *
import pickle
import threading
import random
import copy

config(clock = 'Lamport')
config(handling = 'all')

TIMEOUT=1

class Replica(process):
    def setup(replica_id:int,curr_pr,ps:list,f:int,number_of_requests:int):
    # ====== attributes of Replica ======
        output("creating replica ", replica_id)
        self.f = f
        self.replicas=ps
        self.proposals=set()
        self.number_of_requests = number_of_requests
        self.processing_req=False
        self.votes_received=0
        random.seed(6)
    # ====== attributes of Main ======
        self.replica_id = replica_id
        self.window_size = 1
        self.id = id
        self.win_sz = 1
        self.curr_pr = curr_pr


    # ====== attributes of MemPool ======
        self.q = deque()


    # ====== attributes of Ledger ======

        self.node_id = self.id
        self.file_name = os.path.abspath(cur_path + "/../../data/Ledger_" + str(self.node_id) + ".txt")
        self.pending_map = {}
        self.commited_blocks = deque()  # committed block with window size
        self.ledger_state = ""

    # ====== attributes of Safety ======
        #self.private_key = private_key
        self.highest_vote_round = -1
        self.highest_qc_round = -1

        self.private_key = private_key
        self.replica_public_keys = replica_public_keys
        self.client_public_keys = client_public_keys


    # ====== attributes of BlockTree ======


        self.pending_block_tree = set()
        self.pending_votes = defaultdict(list)
        vote_info = VoteInfo(-1, -1, -2, -2)
        ledger_commit_info = LedgerCommitInfo(None,vote_info)
        qc = QC(vote_info, ledger_commit_info)
        genesis_block = Block(0, -1, "", qc)
        self.high_qc = qc
        self.high_commit_qc = qc


    # ====== attributes of PaceMaker ======
        self.current_round = 0
        self.last_round_tc = None
        self.pending_timeouts = None
        self.delta = 1
        self.timer = threading.Timer(None, None)
        self.ps = ps

    # ====== attributes of LeaderElection ======
        self.exclude_size = f  # f to 2f
        self.reputation_leaders = {}



    # ====== methods of Main ======


    def Main_current_leader(self):
        return id == self.leader_election.get_leader()

    def Main_can_send(self):
        print("can_send is, ", self.leader_election.get_leader(self.pacemaker.current_round) == self.id)
        print(self.pacemaker.current_round , self.id)
        return self.leader_election.get_leader(self.pacemaker.current_round) == self.curr_pr
        # return self.leader_election.get_leader(self.pacemaker.current_round) == self.id

    def Main_start_event_processing(self, message, type):
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

    def Main_process_certificate_qc(self, qc):
        self.block_tree.process_qc(qc)
        #print("process qc done")
        self.leader_election.update_leader(qc)
        #print("leader election done")
        self.pacemaker.advance_round_qc(qc)
        #print("advance round done")

    def Main_process_proposal_msg(self, P):
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

    def Main_process_timeout_message(self, M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc = self.pacemaker.process_remote_timeout(M)
        if (tc):
            self.pacemaker.advance_round_tc(tc)
            return self.process_new_round_event(tc), self.leader_election.get_leader(self.pacemaker.current_round)

    def Main_process_new_round_event(self, last_tc=None):
        # import pdb; pdb.set_trace()
        u = self.leader_election.get_leader(self.pacemaker.current_round)
        if self.curr_pr == u:
            b = self.block_tree.generate_block(u, self.mempool.get_transactions(), self.pacemaker.current_round)
            p = ProposalMsg(b, last_tc, self.block_tree.high_commit_qc, u)
        # return pickle.dumps(p), self.leader_election.get_leader(self.pacemaker.current_round)
            return p
        # return None

    def Main_process_vote_msg(self, M):
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

    def Main_workload_exists(self):
        if (self.mempool.get_transactions()):
            return True
        else:
            return False

    def Main_add_to_Mempool(self, M):
        self.mempool.add_to_queue(M)


    # ====== methods of MemPool ======


    def MemPool_get_transactions():
        #print("Get Transactions")
        await(len(self.q))
        if len(self.q):
            a = self.q.popleft()
            self.q.appendleft(a)
            return a[1]
        return None

    def MemPool_increment_txn_start_num():
        #print("Popped from queue")
        self.q.popleft()
        return

    def MemPool_add_to_queue( M):
        #print("Added to queue in", M,replica_id)
        self.q.append(M)
        q_not_empty=True
        return

    def MemPool_pop_txns_on_proposal(txns):
        if len(self.q):
            a = self.q.popleft()[1]
            #print(a)
            if(a!=txns):
                self.q.appendleft(a)
        return




    # ====== methods of Ledger ======


    def Ledger_speculate(self, prev_block_id, block_id, payload, block):
        # if block_id in self.pending_map:
        # import pdb; pdb.set_trace()
        self.pending_map[block_id] = {
            "prev_block_id": prev_block_id,
            "block": block
        }
        # pass

    def Ledger_pending_state(self, block_id):
        # import pdb; pdb.set_trace()
        if (block_id in self.pending_map):
            if (self.pending_map[block_id]["prev_block_id"] is not None):
                return self.pending_map[block_id]["prev_block_id"]
            else:
                return None
        else:
            return None

    def Ledger_commit(self, block_id):
        # update start txn after commit
        file = open(self.file_name, "a+")
        # import pdb; pdb.set_trace()
        if block_id in self.pending_map:
            # print("node_id is ", self.node_id, " , round is ", self.pending_map[block_id]["block"].round)
            file.write(self.pending_map[block_id]["block"].payload)
            file.close()
            self.add_committed_block_to_Q(block_id)
            # self.ledger_state = hash(self.ledger_state +"||"+ self.pending_map[block_id]["payload"])
            # self.pending_map = {}
            self.pending_map.pop(block_id)
            # TODO: look at above two lines to complete code

        # pass

    def Ledger_committed_block(self, block_id):
        # import pdb; pdb.set_trace()
        for di in self.commited_blocks:
            if block_id in di:
                return di[block_id]
        return None

    def Ledger_add_committed_block_to_Q(self, block_id):
        # import pdb; pdb.set_trace()
        if len(self.commited_blocks) == self.window_size:
            self.commited_blocks.popleft()
        self.commited_blocks.append(self.pending_map[block_id].copy())


    # ====== methods of Safety ======


    def Safety_update_highest_qc_round(self, qc_round):
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    def Safety_consecutive(self, block_round, round):
        return round + 1==block_round

    def Safety_safe_to_extend(self, block_round, qc_round, tc):
        if tc is not None:
            return self.consecutive(block_round, tc.round) and qc_round >= max(tc.tmo_high_qc_rounds)
        return True

    def Safety_safe_to_vote(self, block_round, qc_round, tc):
        if (block_round <= max(self.highest_vote_round, qc_round)):
            return False
        return self.consecutive(block_round, qc_round) or self.safe_to_extend( block_round, qc_round, tc)

    def Safety_safe_to_timeout(self, round, qc_round, tc):
        if (qc_round < self.highest_qc_round or round <= max(self.highest_vote_round - 1, qc_round)):
            return False
        return self.consecutive( round, qc_round) or self.consecutive( round, tc.round)

    def Safety_commit_state_id_candidate(self, block_round, qc, block):
        if (self.consecutive(block_round, qc.vote_info.round) and qc.vote_info.round >=0):
            return self.ledger.pending_state(block.id)
        else:
            return None

    def Safety_valid_signatures(self, high_qc, last_tc):
        i=0
        if(high_qc.vote_info.round==-1):
            return True
        for signature in high_qc.signatures:
            if self.verify_signature(signature.id,signature.message,signature.type):
                i+=1
        if(i==2):
            return True
        else:
            return False


    def Safety_verify_signature(self, id, message, type='replica'):
        if type == "replica":
            v_key = VerifyKey(self.replica_public_keys[id],
                              encoder=HexEncoder)
        elif type == 'client':
            v_key = VerifyKey(self.clients_public_keys[id],
                              encoder=HexEncoder)
        try:
            v_key.verify(message)
        except BadSignatureError:
            return False
        except:
            return False

        return True

    def Safety_make_signature(self,block):
        return Signature(self.id,self.private_key.sign(block.payload.encode('utf-8')),'replica')

    def Safety_make_vote(self, block, last_tc, high_commit_qc):
        # import pdb; pdb.set_trace()
        #print(block)
        qc_round = block.qc.vote_info.round
        # import pdb; pdb.set_trace()
        if (self.valid_signatures(high_commit_qc, last_tc) and self.safe_to_vote(block.round, qc_round, last_tc)):
            self.update_highest_qc_round(qc_round)
            self.increase_highest_vote_round(block.round)
            signature=self.make_signature(block)
            vote_info = VoteInfo(block.id, block.round, block.qc.vote_info.id, qc_round)
            ledger_commit_info = LedgerCommitInfo(self.commit_state_id_candidate(block.round, block.qc, block), vote_info)
            return VoteMsg(vote_info, ledger_commit_info, high_commit_qc, sender=self.id, signature=signature)
        return None


    def Safety_make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if (self.valid_signatures(high_qc, last_tc) and self.safe_to_timeout(round, qc_round, last_tc)):
            return TimeoutInfo(round, high_qc, self.curr_pr, Signature(self.id,self.private_key.sign(str((round, high_qc.vote_info.round)).encode('utf-8')),'replica'))
        return None

    # ====== methods of BlockTree ======


    def BlockTree_process_qc(self, qc):
        if qc.ledger_commit_info.commit_state_id is not None:
            self.ledger.commit(qc.vote_info.parent_id)
            self.high_commit_qc = self.get_max_QC(qc, self.high_commit_qc)
        self.high_qc = self.get_max_QC(qc, self.high_qc)


    def BlockTree_execute_and_insert(self, proposal):
        self.ledger.speculate(proposal.block.qc.vote_info.id, proposal.block.id, proposal.block.payload, proposal.block)
        self.pending_block_tree.add(proposal.block)

    def BlockTree_process_vote(self, v):
        self.process_qc(v.high_commit_qc)

        vote_idx = str(v.ledger_commit_info.commit_state_id) + str(v.ledger_commit_info.vote_info_hash)
        if (self.safety.verify_signature(v.signature.id, v.signature.message, v.signature.type)):
            self.pending_votes[vote_idx].append(v.signature)

        if self.pending_votes[vote_idx] and len(self.pending_votes[vote_idx]) == 2:
            qc = QC(vote_info=v.vote_info, ledger_commit_info=v.ledger_commit_info,
                    signatures=self.pending_votes[vote_idx].copy())
            return qc
        return None

    def BlockTree_generate_block(self, u, txns, current_round):
        return Block(author=u, round=current_round, payload=txns, qc=self.high_qc)

    def BlockTree_get_max_QC(self, qc1, qc2):
        maxQC = qc1 if (qc1.vote_info.round > qc2.vote_info.round) else qc2
        return maxQC

    # ====== methods of PaceMaker ======


        def PaceMaker_stop_timer(self, round):
        self.timer.cancel()
        pass

    def PaceMaker_get_round_timer(self, r):
        # c=logical_clock()
        return 4 * self.delta

    def PaceMaker_start_timer(self, new_round):
        # self.stop_timer(self.current_round)
        print("current_round is, ", new_round)
        self.current_round = new_round
        # self.timer = threading.Timer(self.get_round_timer(new_round), self.local_timeout_round)
        # self.timer.start()
        # return self.get_round_timer(self, self.current_round)

    def PaceMaker_local_timeout_round(self):
        # save_consensus_state()
        print("local timeout")
        self.stop_timer(self.current_round) ## TODO: check if this is wrong or right
        print("stopped timer")
        timeout_info = self.safety.make_timeout(self.current_round, self.block_tree.high_qc, self.last_round_tc)
        print("local_timeout done")
        # broadcast TimeoutMsg(timeout_info,self.last_round_tc,self.block_tree.high_commit_qc)
        time_out_msg = TimeoutMsg(timeout_info,self.last_round_tc,self.block_tree.high_commit_qc)
        c = logical_clock()
        send(('time_out_msg',time_out_msg,c),to=ps)

    def PaceMaker_process_remote_timeout(self, tmo):
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
                return TC(round = round, tmo_high_qc_rounds=tmo_high_qc_rounds, tmo_signatures=signatures)
        return None

    def PaceMaker_advance_round_tc(self, tc):
        if (tc is None or tc.round < self.current_round):
            return False
        self.last_round_tc = tc
        self.stop_timer(self.current_round)
        self.start_timer(tc.round + 1)
        return True

    def PaceMaker_advance_round_qc(self, qc):
        # import pdb; pdb.set_trace()
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.stop_timer(self.current_round)
        self.start_timer(qc.vote_info.round + 1)
        return True


    # ====== methods of LeaderElection ======


    def LeaderElection_elect_reputation_leader(self, qc):
        # import pdb; pdb.set_trace()
        active_validators = set()
        last_authors = set()
        current_qc = qc
        i = 0
        while i < self.window_size:# or len(last_authors) < self.exclude_size:
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            # if not current_block:
            #     return self.ps[random.randint(0, len(self.ps) - 1)]
            block_author = current_block.author if current_block else None
            signers=set()
            # import pdb; pdb.set_trace()
            if current_qc.signatures:
                for signature in current_qc.signatures:
                    signers.add(self.ps[signature.id])
            else:
                signers = signers.union(self.ps)
            if i < self.window_size:
                active_validators.update(signers)
            if len(last_authors) < self.exclude_size and block_author is not None:
                last_authors.add(block_author)
            if current_block:
                current_qc = current_block.qc
            i += 1
        active_validators = active_validators.difference(last_authors)
        # print("active_validators is ", active_validators)
        rand_index = random.randint(0, len(active_validators) - 1)
        # import pdb; pdb.set_trace()
        print("leader index in ", self.ledger.node_id , " is ", rand_index)
        return list(active_validators)[rand_index]

    def LeaderElection_update_leader(self, qc):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = self.pacemaker.current_round
        if extended_round + 1 == qc_round and qc_round + 1 == current_round:
            # import pdb; pdb.set_trace()
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def LeaderElection_get_leader(self, round):
        #print("round",round)
        # import pdb; pdb.set_trace()
        # if self.reputation_leaders and round in self.reputation_leaders:
        #     return self.reputation_leaders[round]
        # return self.ps[int((round / 2) % len(self.ps))]
        return self.ps[int((round) % len(self.ps))]




    # ====== methods of Validator ======


    def receive(msg=('proposal',p1,c1)):
        c2=logical_clock()
        output("recieved proposal message in",replica_id)
        send(('proposal ack',c2), to=replicas)
        self.Main_start_event_processing(p1,'proposal_message')


    def receive(msg=('vote',vote_info,c1)):
        #check if received replica is leader using PaceMaker
        print("votes received before check",votes_received)
        if received_suf_votes():
            return
        output("votes_received",votes_received," in replica",replica_id)
        votes_received = votes_received + 1
        c2=logical_clock()
        output("recieved vote in leader ",replica_id)
        self.Main_start_event_processing(vote_info,'vote_message')


    def receive(msg=('request',cmd,c,p)):
        output("message received "+str(cmd)+" from "+str(p)+" at "+str(replica_id))
        M=('request',cmd,c)
        self.Main_add_to_Mempool(M)

    def run():
        #handle first round
        time.sleep(5)
        if(self.Main_can_send()):
            #output("sending messages to all processes from replica",replica_id)
            self.Main_process_new_round_event(TC(-10))
            -- l2
           # processed_votes=0

        while(1):  # keep replica always running
            -- handlemessages
            if(self.Main_can_send()):

                while(votes_received<=2*f+1):
                    --  handlevotes   #handle 2f+1 votes before

        output("Replica ", replica_id," is terminated")


    def received_suf_votes():
        return votes_received>=2*f+1

