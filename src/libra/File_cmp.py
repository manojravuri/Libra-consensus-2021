import filecmp
import os

def main():
    Ledger_files=7
    flag=True
    for i in range(Ledger_files-1):
        dir = os.path.dirname(os.path.dirname(os.getcwd())) + '/data/'

        if not filecmp.cmp(dir+'Ledger_0.txt', dir+'Ledger_'+str(i+1)+'.txt'):
            print("File contents are different: in Ledger_0.txt and ",'Ledger_'+str(i+1)+'.txt')
            flag=False

    if flag:
        print("All the Ledgers contents match")

if __name__ == "__main__":
    main()