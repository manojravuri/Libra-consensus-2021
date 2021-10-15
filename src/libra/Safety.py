from Ledger import Ledger
from Objects import *


from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

class Safety:
    def __init__(self,id, ledger, highest_vote_round=-1, highest_qc_round=-1,private_key=None,replica_public_keys=None,client_public_keys=None, curr_pr = None):
        self.id=id
        self.private_key = private_key
        self.replica_public_keys = replica_public_keys
        self.client_public_keys = client_public_keys
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
        self.ledger = ledger
        self.curr_pr = curr_pr

    def increase_highest_vote_round(self, round):
        self.highest_vote_round = max(round, self.highest_vote_round)

    def update_highest_qc_round(self, qc_round):
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    def consecutive(self, block_round, round):
        return round + 1==block_round

    def safe_to_extend(self, block_round, qc_round, tc):
        if tc is not None:
            return self.consecutive(block_round, tc.round) and qc_round >= max(tc.tmo_high_qc_rounds)
        return True

    def safe_to_vote(self, block_round, qc_round, tc):
        if (block_round <= max(self.highest_vote_round, qc_round)):
            return False
        return self.consecutive(block_round, qc_round) or self.safe_to_extend( block_round, qc_round, tc)

    def safe_to_timeout(self, round, qc_round, tc):
        if (qc_round < self.highest_qc_round or round <= max(self.highest_vote_round - 1, qc_round)):
            return False
        return self.consecutive( round, qc_round) or self.consecutive( round, tc.round)

    def commit_state_id_candidate(self, block_round, qc, block):
        if (self.consecutive(block_round, qc.vote_info.round) and qc.vote_info.round >=0):
            return self.ledger.pending_state(block.id)
        else:
            return None

    def valid_signatures(self, high_qc, last_tc):
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


    def verify_signature(self, id, message, type='replica'):
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

    def make_signature(self,block):
        return Signature(self.id,self.private_key.sign(block.payload.encode('utf-8')),'replica')

    def make_vote(self, block, last_tc, high_commit_qc):
        # import pdb; pdb.set_trace()
        #print(block)
        qc_round = block.qc.vote_info.round
        # import pdb; pdb.set_trace()
        if (self.valid_signatures(high_commit_qc, last_tc) and self.safe_to_vote(block.round, qc_round, last_tc)):
            #print(1)
            self.update_highest_qc_round(qc_round)
            #print(2)
            self.increase_highest_vote_round(block.round)
            #print(3)
            #print(block, block.id)
            signature=self.make_signature(block)
            # import pdb; pdb.set_trace()
            vote_info = VoteInfo(block.id, block.round, block.qc.vote_info.id, qc_round)
            #print(4)
            ledger_commit_info = LedgerCommitInfo(self.commit_state_id_candidate(block.round, block.qc, block), vote_info)
            #print(5)
            return VoteMsg(vote_info, ledger_commit_info, high_commit_qc, sender=self.id, signature=signature)
        return None


    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if (self.valid_signatures(high_qc, last_tc) and self.safe_to_timeout(round, qc_round, last_tc)):
            return TimeoutInfo(round, high_qc, self.curr_pr, Signature(self.id,self.private_key.sign(str((round, high_qc.vote_info.round)).encode('utf-8')),'replica'))
        return None
