import linecache


class MemPool:

    def __init__(self, txns_cnt=10):
        self.txns_cnt = txns_cnt
        self.start_line = 1

        file = open("transactions.txt", "r")
        self.num_lines = 0
        content = file.read()
        coList = content.split("\n")

        for i in coList:
            if i:
                self.num_lines += 1
        file.close()
        pass

    def get_transactions(self):
        # extracting the 5th line
        txns = []
        if self.start_line + self.txns_cnt <= self.num_lines:
            for i in range(self.start_line, self.start_line + self.txns_cnt):
                line = linecache.getline('transactions.txt', i)
                txns.append(line.strip())
        else:
            for i in range(self.start_line, self.num_lines):
                line = linecache.getline('transactions.txt', i)
                txns.append(line.strip())
        linecache.clearcache()
        return txns
