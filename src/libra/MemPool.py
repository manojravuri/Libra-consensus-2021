import linecache
import sys
import pathlib
import os


class MemPool:

    def __init__(self, txns_cnt=10):
        self.txns_cnt = txns_cnt
        self.start_line = 1

        cur_path = os.path.dirname(__file__)
        absolute = os.path.abspath(cur_path+"/../../data/transactions.txt")
        self.file_name = absolute

        file = open(self.file_name, "r")
        self.num_lines = 0
        content = file.read()
        coList = content.split("\n")

        for i in coList:
            if i:
                self.num_lines += 1
        file.close()
        pass

    def get_transactions(self):
        txns = []
        end_line = min(self.start_line + self.txns_cnt, self.num_lines)
        for i in range(self.start_line, end_line):
            line = linecache.getline(self.file_name, i)
            txns.append(line.strip())
        linecache.clearcache()
        print("transactions",txns)
        return txns
