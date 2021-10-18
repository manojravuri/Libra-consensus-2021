An implementation of DiemBFT v4 based on-

DiemBFT v4: State Machine Replication in the Diem Blockchain by The Diem Team at Facebook

The described system has 3f+1 replicas which will tolerate f failures, we will change type of failures based on the probability of failure types or we can hardcode the failures

Motivation

This was done as course project for the course CSE 535 Distributed Systems at Stony Brook University taught by Professor Scott Stoller.

The system is structured in following way: A startup process (bcr.da) reads the configuration file provided as commandline argument and creates Olympus and clients as mentioned in the configuration file. The Olympus after starting created the replicas based on the value of fault tolerance. The clients get their workload from the configuration file. Clients and replicas depend upon the Olympus to create the keys for signing. The public keys of all elements are shared on request. Fault Injection: If failure and triggers are mentioned in the configuration file then the necessary failures are injected during runtime in replicas when the trigger occurs.

The system is structured as follows: The startup process (Root.da) will read the configuration of Clients (Client.da) and Replicas (Replica.da) from the text file we give in as an input which loads the workload.
The Root module will read and start the Clients with specifications and the Replicas with the given specifications.

The client will generate random requests and send it to the replicas and the replicas will try to form a consensus and then commit the requests to their local ledgers and exit on succesfull completion of all requests.

Used DistAlgo for the creation of async clients and message passing.

PLATFORM
OS: Mac OSX
DistAlgo version: 1.0.9 TODO: change this version
Python implementation: CPython TODO: change this
Python version: 3.7.12

INSTRUCTION
1. Download the relevant python and distalgo release.
2. Unzip the release zip in your PC. Install the requirements in requirements.txt using pip install -r requirements.txt.
3. Put your config file in config folder.
4. Open a command line terminal.
5. Change your current directory to <DAROOT>/src
6. In the terminal, run the following command
    python -m da -m libra.Root <path to your config file>

For example to run config2 file:
1. open a command line terminal after installing relevant distributions.
2. cd to <DAROOT>/src
2. on the terminal run:
    python -m da -m libra.Root libra/config/config2.txt

WORKLOAD GENERATION
We use config files to generate the relevant workload. The client files are present in libra_blockchain/src/libra/config folders.

The code pulls up the file passed as argument and sets up the client, replicas accordingly.

You run python -m da -m libra.Root libra/config/config2.txt to set up the system with configurations in config2.txt


LOGS
Once you run the relevant test case, then the logs with what is happening would come up in <DAROOT>/logs (for client and replica logs).

The commits happening on each node would be written to text files, which are present in <DAROOT>/data (indexed with the node id)


TIMEOUTS
For timeouts, we used python threading module.

Each round will wait for a 4*delta time and if no operation is done, it will process a local timeout.

BUGS and LIMITATIONS

LeaderElection:
1. We are doing leader election in a round-robin system.

Timeouts:
1. When a TC is generated, we are running into an infinite loop.


MAIN FILES

src/libra/Root.da
src/libra/Client.da
src/libra/Replica.da
src/libra/Objects.py

CODE SIZE
non-blank non-comment lines of code  = 766
algorithm  = 403
other = 161
comments = 202

LANGUAGE FEATURE USAGE
list comprehensions  = 24
dictionary comprehensions = 18
set comprehensions = 10
await statements = 12
recieve handlers = 7


CONTRIBUTIONS
Nihal Goalla: pseudocode, documentation, client.da, timeouts methodology.
Manoj Ravuri: Signatures, Replica.py, Main.py, modules in python,
Rohith Vaddavalli: Replica.da, logging, Root.da, Ledger methodology
