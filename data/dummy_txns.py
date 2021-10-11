f = open("../transactions.txt", "w")
for i in range(250):
    f.write("Txn:"+str(i)+"\n")
f.close()
