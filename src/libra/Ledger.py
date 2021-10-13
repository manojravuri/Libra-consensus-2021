from .MemPool import MemPool
import os
import copy

class Ledger:
    def __init__(self, id, mempool):
        self.node_id = id
        self.mempool = mempool
        cur_path = os.path.dirname(__file__)
        self.file_name=os.path.abspath(cur_path + "/../../data/Ledger_"+str(self.node_id)+".txt")
        self.pending_map={}
        self.current_ledger = {}
        pass

    def speculate(self, prev_block, block, txns):
        self.pending_map[block.id]={
            "curr_block":block,
            "prev_block":prev_block,
            "txns":txns
        }
        pass

    def pending_state(self, block_id):
        pass

    def commit(self, block_id):
        # update start txn after commit
        self.file = open(self.file_name, "w")
        self.file.write(str(block_id)+":"+self.pending_map[block_id]["prev_block_id"]+"||"+self.pending_map[block_id]["txns"])
        self.file.close()
        pending_map_copy = copy.deepcopy(self.pending_map)
        self.pending_map={}
        self.current_ledger.update(pending_map_copy)
        self.mempool.increment_txn_start_num()
        # pass
    def custom_commit_block(self, block):
        self.current_ledger[block.id] = {
        "curr_block": block,
        "prev_block": None,
        "txns":""
        }

    def committed_block(self, block_id):
        if block_id in self.pending_map:
            return self.pending_map[block_id]
        elif block_id in self.current_ledger:
            return self.current_ledger[block_id]
        return None
        # pass
