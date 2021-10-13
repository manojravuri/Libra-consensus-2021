from collections import deque

from .MemPool import MemPool
import os
import copy


class Ledger:
    def __init__(self, id, mempool, window_size):
        self.node_id = id
        self.mempool = mempool
        cur_path = os.path.dirname(__file__)
        self.file_name = os.path.abspath(cur_path + "/../../data/Ledger_" + str(self.node_id) + ".txt")
        self.pending_map = {}
        self.window_size = window_size
        self.commited_blocks = deque()  # committed block with window size
        self.ledger_state = ""
        pass

    def speculate(self, prev_block_id, block_id, block):
        self.pending_map[block_id] = {
            "prev_block_id": prev_block_id,
            "block": block,
        }
        pass

    def pending_state(self, block_id):
        return self.pending_map[block_id]["block"].payload

    def commit(self, block_id):
        # update start txn after commit
        file = open(self.file_name, "w")
        file.write(self.pending_map[block_id]["block"].payload)
        file.close()
        self.add_committed_block_to_Q(block_id)
        self.ledger_state = hash(self.ledger_state +"||"+ self.pending_map[block_id]["block"].payload)
        self.pending_map = {}

        # pass

    def committed_block(self, block_id):
        for di in self.commited_blocks:
            if block_id in di:
                return di[block_id]
        return None

    def add_committed_block_to_Q(self, block_id):
        if len(self.commited_blocks) == self.window_size:
            self.commited_blocks.popleft()
        self.commited_blocks.append(self.pending_map[block_id])
