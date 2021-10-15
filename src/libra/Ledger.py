from collections import deque, defaultdict

from MemPool import MemPool
import os
import copy


class Ledger:
    def __init__(self, id, mempool, window_size):
        self.node_id = id
        self.mempool = mempool
        cur_path = os.path.dirname(__file__)
        self.file_name = os.path.abspath(cur_path + "/../../data/Ledger_" + str(self.node_id) + ".txt")
        # self.file_name = os.path.abspath("/Users/nihalgoalla/Documents/Fall21/CSE535/libra_blockchain/data/Ledger_" + str(self.node_id) + ".txt")
        self.pending_map = {}
        self.window_size = window_size
        self.commited_blocks = deque()  # committed block with window size
        self.ledger_state = ""
        # pass

    def speculate(self, prev_block_id, block_id, payload, block):
        # if block_id in self.pending_map:
        # import pdb; pdb.set_trace()
        self.pending_map[block_id] = {
            "prev_block_id": prev_block_id,
            "block": block
        }
        # pass

    def pending_state(self, block_id):
        # import pdb; pdb.set_trace()
        if (block_id in self.pending_map):
            if (self.pending_map[block_id]["prev_block_id"] is not None):
                return self.pending_map[block_id]["prev_block_id"]
            else:
                return None
        else:
            return None

    def commit(self, block_id):
        # update start txn after commit
        file = open(self.file_name, "a+")
        # import pdb; pdb.set_trace()
        if block_id in self.pending_map:
            # print("node_id is ", self.node_id, " , round is ", self.pending_map[block_id]["block"].round)
            file.write(self.pending_map[block_id]["block"].payload)
            file.close()
            self.add_committed_block_to_Q(block_id)
            # self.ledger_state = hash(self.ledger_state +"||"+ self.pending_map[block_id]["payload"])
            # self.pending_map = {}
            self.pending_map.pop(block_id)
            # TODO: look at above two lines to complete code

        # pass

    def committed_block(self, block_id):
        # import pdb; pdb.set_trace()
        for di in self.commited_blocks:
            if block_id in di:
                return di[block_id]
        return None

    def add_committed_block_to_Q(self, block_id):
        # import pdb; pdb.set_trace()
        if len(self.commited_blocks) == self.window_size:
            self.commited_blocks.popleft()
        self.commited_blocks.append(self.pending_map[block_id].copy())
