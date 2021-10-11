from libra.MemPool import MemPool
import os

class Ledger:
    def __init__(self, id, mempool):
        self.node_id = id
        self.mempool = mempool
        cur_path = os.path.dirname(__file__)
        self.file_name=os.path.abspath(cur_path + "/../../data/Ledger_"+str(self.node_id)+".txt")
        self.pending_map={}
        pass

    def speculate(self, prev_block_id, block_id, txns):
        self.pending_map[block_id]={
            "prev_block_id":prev_block_id,
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
        self.pending_map={}
        self.mempool.increment_txn_start_num()
        pass

    def committed_block(self, block_id):
        pass
