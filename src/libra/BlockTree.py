from .Ledger import Ledger
from collections import defaultdict

class BlockTree:
    def __init__(self, ledger, pending_block_tree = set(), pending_votes = defaultdict(list), high_qc = None, high_commit_qc = None):
        self.ledger = ledger
        self.pending_block_tree = pending_block_tree
        self.pending_votes = pending_votes
        vote_info = VoteInfo(-1,-1,-2,-2)
        ledger_commit_info = LedgerCommitInfo()
        qc = QC(vote_info, ledger_commit_info)
        genesis_block = Block(0, -1, "", QC())
        qc.block = genesis_block
        self.high_qc = qc
        self.high_commit_qc = qc
        ledger.custom_commit_block(self.high_qc.block)

    def process_qc(self, qc):
        print('qc is ', qc)
        if(qc and qc.ledger_commit_info and qc.ledger_commit_info.commit_state_id):
            self.ledger.commit(self, qc.vote_info.parent_id)
            self.pending_block_tree.prune(qc.vote_info_parent_id)
            self.high_commit_qc=max(qc, self.high_commit_qc)
            self.high_qc=max(qc, self.high_qc)
        # print("process qc done")


    def execute_and_insert(self,b):
        # print(b)
        if (b and b.qc):
            self.ledger.speculate(b.qc.block,b,b.payload)
            self.pending_block_tree.add(b)

    def process_vote(self,v):
        print("in process_vote ", v)
        self.process_qc(v.high_commit_qc)
        print("1")
        vote_idx=(v.ledger_commit_info.vote_info_hash.round)
        print("vote_idx is , ", vote_idx)
        print("2")
        self.pending_votes[vote_idx].append(v.signature)
        print("self.pending_votes[vote_idx] is , ", self.pending_votes[vote_idx])
        print("3")
        if(self.pending_votes[vote_idx] and len(self.pending_votes[vote_idx])==7):
            print("in if loop")
            # qc=QC(vote_info=v.vote_info,state_id=v.state_id,votes=self.pending_votes[vote_idx])
            qc=QC(vote_info=v.vote_info,votes=self.pending_votes[vote_idx])
            return qc
        return None

    def generate_block(self,u,txns,current_round,high_qc):
        return Block(author=u,round=current_round,payload=txns,qc=high_qc)







class VoteInfo:
    def __init__(self,id,round,parent_id,parent_round):
        self.id=id
        self.round=round
        self.parent_id=parent_id
        self.parent_round=parent_round
        self.hash_ = str(id) + " " + str(round) + " " + str(parent_id) + " " + str(parent_round)

class LedgerCommitInfo:
    def __init__(self,commit_state_id = None,vote_info_hash = None):
        self.commit_state_id=commit_state_id
        self.vote_info_hash=vote_info_hash


class VoteMsg:
    def __init__(self,vote_info,ledger_commit_info,high_commit_qc,sender,signature):
        self.sender=sender
        self.signature=signature
        self.vote_info=vote_info
        self.ledger_commit_info=ledger_commit_info
        self.high_commit_qc=high_commit_qc


class QC:
    def __init__(self,vote_info = None,ledger_commit_info = None,signatures = None,author = None,author_signature = None, block = None, votes = None, last_tc = None):
        self.vote_info=vote_info
        self.ledger_commit_info=ledger_commit_info
        self.signatures=signatures
        self.author=author
        self.author_signature=author_signature
        self.block = block
        self.votes = votes
        self.last_tc = last_tc

    # def __repr__(self):
    #     return f'{self.author}'

    def __lt__(self, other):
        # p1 < p2 calls p1.__lt__(p2)
        return self.block.round < other.block.round

    def __eq__(self, other):
        # p1 == p2 calls p1.__eq__(p2)
        return self.block.round == other.block.round

class Block:
    def __init__(self,author,round,payload,qc):
        self.author=author
        self.round=round
        self.payload=payload
        self.qc=qc
        self.id=str(author)+str(round)+str(payload)+str(qc)


class TimeoutInfo:
    def __init__(self,round,high_qc,sender,signature):
        self.round=round
        self.high_qc=high_qc
        self.sender=sender
        self.signature=signature


class TC:
    def __init__(self,round,tmo_high_qc_rounds,tmo_signatures):
        self.round=round
        self.tmo_high_qc_rounds=tmo_high_qc_rounds
        self.tmo_signatures=tmo_signatures


class TimeoutMsg:
    def __init__(self,tmo_info,last_round_qc,high_commit_qc):
        self.tmo_info=tmo_info
        self.last_round_qc=last_round_qc
        self.high_commit_qc=high_commit_qc


class ProposalMsg:
    def __init__(self,block,last_round_qc,high_commit_qc,signature, last_round_tc, sender):
        self.block=block
        self.last_round_qc=last_round_qc
        self.high_commit_qc=high_commit_qc
        self.signature=signature
        self.last_round_tc = last_round_tc
        self.sender = sender
