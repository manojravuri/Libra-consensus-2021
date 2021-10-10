import BlockTree,LeaderElection,PaceMaker,Safety,MemPool
from BlockTree import ProposalMsg
class Main:
    def __init__(self):
        self.pacemaker=PaceMaker()
        self.block_tree=BlockTree()
        self.leader_election=LeaderElection()
        self.pacemaker=PaceMaker()
        self.safety=Safety()
        self.mempool=MemPool()

    def start_event_processing(self,M):
        if(M=='local timeout'):
            self.pacemaker.local_timeout_round()
        if(M=='proposal_message'):
            self.process_proposal_msg(M)
        if(M == 'vote message'):
            self.process_vote_msg(M)
        if(M == 'timeout mesaage'):
            self.process_timeout_message(M)


    def process_certificate_qc(self,qc):
        self.block_tree.process_qc()
        self.leader_election.update_leader(qc)
        self.pacemaker.advance_round(qc)

    def process_proposal_msg(self,P):
        self.process_certificate_qc(P.block.qc)
        self.process_certificate_qc(P.high_commit_qc)
        self.pacemaker.advance_round_tc(P.last_round_tc)
        round=self.pacemaker.current_round
        current_round=round
        leader=self.leader_election.get_leader(current_round)
        if(P.block.round != round or P.sender != leader or P.block.author !=leader):
            return
        self.block_tree.execute_and_insert(P)
        vote_msg=self.safety.make_vote(P.block,P.last_round_tc)
        if(vote_msg is not None):
            pass
            #send vote_msg to LeaderElection.get_leader(current_round+1)

    def process_timeout_message(self,M):
        self.process_certificate_qc(M.tmo_info.high_qc)
        self.process_certificate_qc(M.high_commit_qc)
        self.pacemaker.advance_round_tc(M.last_round_tc)
        tc=self.pacemaker.process_remote_timeout(M)
        if(tc is not None):
            self.pacemaker.advance_round_tc(tc)
            self.process_new_round_event(tc)

    def process_new_round_event(self,last_tc):
        if u == self.leader_election.get_leader(self.pacemaker.current_round):
            b = self.block_tree.generate_block(self.mempool.get_transactions(),self.pacemaker.current_round)
            p = ProposalMsg(b,last_tc,self.block_tree.high_commit_qc)
            # broadcast p

    def process_vote_msg(self,M):
        qc=self.block_tree.process_vote(M)
        if(qc is not None):
            self.process_certificate_qc(qc)
            self.process_new_round_event(None)
