from Ledger import Ledger

class BlockTree:
    def __init__(self,pending_block_tree,pending_votes,high_qc,high_commit_qc):
        self.ledger=Ledger()
        self.pending_block_tree=pending_block_tree
        self.pending_votes=pending_votes
        self.high_qc=high_qc
        self.high_commit_qc=high_commit_qc


    def process_qc(self,qc):
        if(qc.ledger_commit_info.commit_state_id is not None):
            self.ledger.commit(self,qc.vote_info.parent_id)
            self.pending_block_tree.prune(qc.vote_info_parent_id)
            self.high_commit_qc=max(qc,self.high_commit_qc)
            self.high_qc=max(qc,self.high_qc)


    def execute_and_insert(self,b):
        self.ledger.speculate(b.qc.block_id,b.id,b.payload)
        self.pending_block_tree.add(b)

    def process_vote(self,v):
        self.process_qc(self,v.high_commit_qc)

    def generate_block(self,txns,current_round):
        return Block()







class VoteInfo:
    def __init__(self,id,round,parent_id,parent_round):
        self.id=id
        self.round=round
        self.parent_id=parent_id
        self.parent_round=parent_round

class LedgerCommitInfo:
    def __init__(self,commit_state_id,vote_info_hash):
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
    def __init__(self,vote_info,ledger_commit_info,signatures,author,author_signature):
        self.vote_info=vote_info
        self.ledger_commit_info=ledger_commit_info
        self.signatures=signatures
        self.author=author
        self.author_signature=author_signature

class Block:
    def __init__(self,author,round,payload,qc,id):
        self.author=author
        self.round=round
        self.payload=payload
        self.qc=qc
        self.id=id


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
    def __init__(self,block,last_round_qc,high_commit_qc,signature):
        self.block=block
        self.last_round_qc=last_round_qc
        self.high_commit_qc=high_commit_qc
        self.signature=signature






