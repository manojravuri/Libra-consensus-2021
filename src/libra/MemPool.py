import os
import time
from collections import deque


class MemPool:

    def __init__(self):
        self.q = deque()
        self.i = 0
        pass

    def get_transactions(self):
        #print("Get Transactions")
        if len(self.q):
            a = self.q.popleft()
            self.q.appendleft(a)
            return a
        self.i += 1
        return str(self.i)
        # return None

    def increment_txn_start_num(self):
        #print("Popped from queue")
        self.q.popleft()
        return

    def add_to_queue(self, M):
        #print("Added to queue in", M)
        self.q.append(M)
        q_not_empty=True
        return

    def is_q_empty(self):
        return not len(self.q)
