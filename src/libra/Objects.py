class VoteInfo:
    def __init__(self, id, round, parent_id, parent_round):
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round


class LedgerCommitInfo:
    def __init__(self, commit_state_id=None, vote_info=None):
        self.commit_state_id = commit_state_id
        self.vote_info_hash = str(vote_info.id) + "||" + str(vote_info.round) + "||" + str(
            vote_info.parent_id) + "||" + str(vote_info.parent_round)


class Signature:
    def __init__(self, id=None, message=None, type=None):
        self.id = id
        self.message = message
        self.type = type

    def __repr__(self):
        return str(self.id) + str(self.message) + str(self.type)


class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc, sender, signature: Signature):
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
        self.id = hash(str(author) + "||" + str(round) + "||" + str(payload) + "||" + str(qc))


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
    def __init__(self, tmo_info=None, last_round_tc=None, high_commit_qc=None):
        self.tmo_info = tmo_info
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc


class ProposalMsg:
    def __init__(self, block, last_round_tc, high_commit_qc, sender):
        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.sender = sender


class Message:
    def __init__(self, type=None, block=None, high_commit_qc=None, last_round_tc=None, tmo_info=None):
        self.type = type
        self.block = block
        self.high_commit_qc = high_commit_qc
        self.last_round_tc = last_round_tc
        self.tmo_info = tmo_info
