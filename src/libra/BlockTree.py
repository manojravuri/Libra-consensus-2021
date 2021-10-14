from Ledger import Ledger
from collections import defaultdict



class BlockTree:
    def __init__(self, ledger, f=1, high_qc=None,high_commit_qc=None):
        self.ledger = ledger
        self.pending_block_tree = set()
        self.pending_votes = defaultdict(list)
        vote_info = VoteInfo(-1, -1, -2, -2)
        ledger_commit_info = LedgerCommitInfo()
        qc = QC(vote_info, ledger_commit_info)
        genesis_block = Block(0, -1, "", qc)
        self.high_qc = qc
        self.high_commit_qc = qc
        self.f = f
        # ledger.custom_commit_block(self.high_qc.block)

    def process_qc(self, qc):
        print('qc is ', str(qc))
        if qc.ledger_commit_info.commit_state_id is not None:
            self.ledger.commit(qc.vote_info.parent_round)
            # prune branches
            # self.pending_block_tree.prune(qc.vote_info_parent_id)
            self.high_commit_qc = self.get_max_QC(qc, self.high_commit_qc)
        self.high_qc = self.get_max_QC(qc, self.high_qc)
        # print("process qc done")

    def execute_and_insert(self, proposal):
        # print(b)
        self.ledger.speculate(proposal.block.qc.vote_info.round, proposal.block.round, proposal.block.payload,proposal.block)
        self.pending_block_tree.add(proposal.block)

    def process_vote(self, v):
        print("in process_vote ", v)
        self.process_qc(v.high_commit_qc)

        vote_idx = hash(v.ledger_commit_info)
        print("vote_idx is , ", vote_idx)

        self.pending_votes[vote_idx].append(v.signature)
        print("self.pending_votes[vote_idx] is , ", self.pending_votes[vote_idx])

        if self.pending_votes[vote_idx] and len(self.pending_votes[vote_idx]) == ( 1):
            qc = QC(vote_info=v.vote_info,ledger_commit_info=v.ledger_commit_info ,signatures=self.pending_votes[vote_idx])
            print("QuorumC", QC)
            return qc
        return None

    def generate_block(self, u, txns, current_round):
        return Block(author=u, round=current_round, payload=txns, qc=self.high_qc)

    def get_max_QC(self, qc1, qc2):
        print("qc1",qc1.vote_info.round)
        print("qc2", qc2.vote_info.round)
        maxQC = qc1 if (qc1.vote_info.round > qc2.vote_info.round) else qc2
        return maxQC



class VoteInfo:
    def __init__(self, id, round, parent_id, parent_round):
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round


class LedgerCommitInfo:
    def __init__(self, commit_state_id=None, vote_info=None):
        self.commit_state_id = commit_state_id
        self.vote_info_hash = hash(vote_info)


class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc, sender, signature):
        self.sender = sender
        self.signature = signature
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.high_commit_qc = high_commit_qc


class QC:
    def __init__(self, vote_info=None, ledger_commit_info=None, signatures=None, author=None, author_signature=None):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature


class Block:
    def __init__(self, author, round, payload, qc):
        self.author = author
        self.round = round
        self.payload = payload
        self.qc = qc
        # self.id = hash(str(author) + "||" + str(round) + "||" + str(payload) + "||" + str(qc))
        self.id = round


class TimeoutInfo:
    def __init__(self, round, high_qc, sender, signature):
        self.round = round
        self.high_qc = high_qc
        self.sender = sender
        self.signature = signature


class TC:
    def __init__(self, round, tmo_high_qc_rounds=None, tmo_signatures=None):
        self.round = round
        self.tmo_high_qc_rounds = tmo_high_qc_rounds
        self.tmo_signatures = tmo_signatures


class TimeoutMsg:
    def __init__(self, tmo_info, last_round_qc, high_commit_qc):
        self.tmo_info = tmo_info
        self.last_round_qc = last_round_qc
        self.high_commit_qc = high_commit_qc


class ProposalMsg:
    def __init__(self, block,last_round_tc, high_commit_qc,sender):
        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.sender=sender


class Message:
    def __init__(self, type=None, block=None, high_commit_qc=None, last_round_tc=None, tmo_info=None):
        self.type = type
        self.block = block
        self.high_commit_qc = high_commit_qc
        self.last_round_tc = last_round_tc
        self.tmo_info = tmo_info
