from libra.Mempool import Mempool


class Ledger:
    def __init__(self, mempool):
        self.mempool = Mempool
        pass

    def speculate(self, prev_block_id, block_id, txns):
        pass

    def pending_state(self, block_id):
        pass

    def commit(self, block_id):
        # update start txn after commit
        self.mempool.increment_txn_start_num()
        pass

    def committed_block(self, block_id):
        pass
