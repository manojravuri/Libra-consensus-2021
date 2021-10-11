import unittest
from src.libra.MemPool import MemPool


class TestStringMethods(unittest.TestCase):

    def test_get_txns(self):
        mempool = MemPool()
        self.assertTrue(len(mempool.get_transactions()), 10)
        print(mempool.get_transactions())


if __name__ == '__main__':
    unittest.main()
