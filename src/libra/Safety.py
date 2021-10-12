from .Ledger import Ledger
from .BlockTree import VoteMsg, VoteInfo, TimeoutInfo, LedgerCommitInfo
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder


class Safety:
    def __init__(self, ledger, private_key=None,all_replica_public_keys=None,all_client_public_keys=None, highest_vote_round=-1, highest_qc_round=-1):
        self.private_key = private_key
        self.all_replica_public_keys=all_replica_public_keys
        self.all_client_public_keys=all_client_public_keys
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
        self.ledger = ledger

    def increase_highest_vote_round(self, round):
        self.highest_vote_round = max(round, self.highest_vote_round)

    def update_highest_qc_round(self, qc_round):
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    def consecutive(self, block_round, round):
        return round + 1

    def safe_to_extednd(self, block_round, qc_round, tc):
        return self.consecutive(self, block_round, tc, round) and qc_round >= max(tc.tmo_high_qc_rounds)

    def safe_to_vote(self, block_round, qc_round, tc):
        if (block_round <= max(self.highest_vote_round, qc_round)):
            return False
        return self.consecutive(self, block_round, qc_round) and self.safe_to_extednd(self, block_round, qc_round, tc)

    def safe_to_timeout(self, round, qc_round, tc):
        if (qc_round < self.highest_qc_round or round <= max(self.highest_vote_round - 1, qc_round)):
            return False
        return self.consecutive(self, round, qc_round) or self.consecutive(self, round, tc.round)

    def commit_state_id_candidate(self, block_round, qc):
        if (self.consecutive(block_round, qc.vote_info.round)):
            return self.ledger.pending_state(qc.id)
        else:
            return None

    def valid_signatures(self, high_qc, last_tc):
        return True

    def verify_signature(self,id,message,type='replica'):
        if type == "replica":
            v_key = VerifyKey(self.all_replicas_public_keys[id],
                                           encoder=HexEncoder)
        elif type == 'client':
            v_key = VerifyKey(self.all_clients_public_keys[id],
                                           encoder=HexEncoder)
        try:
            v_key.verify(message)
        except nacl.exceptions.BadSignatureError:
            return False
        except:
            return False

        return True

    def make_vote(self, b, last_tc, high_commit_qc):
        # import pdb; pdb.set_trace()
        print(b)
        qc_round = b.qc.vote_info.round
        if self.valid_signatures(b, last_tc) or safe_to_vote(b.round, qc_round, last_tc):
            print(1)
            self.update_highest_qc_round(qc_round)
            print(2)
            self.increase_highest_vote_round(b.round)
            print(3)
            print(b, b.id)
            vote_info = VoteInfo(b.id, b.round, b.qc.vote_info, qc_round)
            print(4)
            ledger_commit_info = LedgerCommitInfo(self.commit_state_id_candidate(b.round, b.qc), vote_info)
            print(5)
            return VoteMsg(vote_info, ledger_commit_info, high_commit_qc, None, None)
        return None

    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if (self.valid_signatures(high_qc, last_tc) and self.safe_to_timeout(round, qc_round, last_tc)):
            return TimeoutInfo(round, high_qc)
        return None
