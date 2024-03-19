### Transactions and Commits
- with auto-commit on, queries will be executed to the DB immediately
- with auto-commit off, nothing will be written until you use the `COMMIT` command
- ![](assets/2024-03-17-17-18-56.png)
- transactions are *atomic*
  - either all of the operations in transaction are completed successfully + committed to the RDBMS, or none of them are
    - if error occurs during transaction, it aborts, and all changes are *rolled back*
      - errors include: data integrity failure, constraint failure, other errors (division by zero), disk failure, system/power outage, etc
    - statements and operations are held in a buffer before `COMMIT` is called
- transactions must maintain database *consistency*
  - consistency - maintain some constraint on the data s.t. we do not end up with more/less data than we started with
- *isolation* - concurrent transactions operate independently and does not interfere with each other
  - maximizes consistency in the face of concurrency
- *durability* - once transaction is committed, the data must be safe from system failures

### ACID
- transactions are ACID compliant if they guarantee the following:
  - ![](assets/2024-03-17-17-30-59.png)
- provides high consistency
- RDBMS **must** maintain ACID guarantees
  - most NoSQL DBs do not

### BASE
- Basically Available Soft-state Eventually consistent
  - provides high availability and eventual consistency
    - e.g. Cassandra's gossip model
  - *soft-state* means we don't actually know when the data will be consistent
- NoSQL transaction satisfy this
  - since NoSQL often distributed, not able to be always consistent 100%
- transaction model guarantees BASE if it guarantees the following
  - ![](assets/2024-03-17-17-52-32.png)

### Strict ACID
- ![](assets/2024-03-17-17-54-30.png)
- airplane seating example:
  - ![](assets/2024-03-17-18-04-19.png)
  - let S1 be old seat and S2 be new seat
    - want to mark S1 as false and S2 as true
    - ```
        Transaction
        read(S1)
        S1 = false
        write(S1)
        read(S2)
        S2 = true
        write(S2)
        commit
        ```
-  ![](assets/2024-03-17-18-45-27.png)
-  ![](assets/2024-03-17-18-45-39.png)
-  ![](assets/2024-03-17-18-45-49.png)
-  *concurrency* is multiple transactions sharing a resource (interleavingly) while *parallelism* is two transaction literally execute at the same time (e.g. on multicore CPU)
-  a schedule of trqansactions is *serial* if each transaction executes fully before another begins
   -  no interleaving operations
   -  *guarantees* consistency, but little concurrency
      -  concurency reduces waiting time => improves throughput
-  *conflict serializable schedule* - the schedule is either serial, or it is equivalent in result to a serial scheudule
   -  if a concurrent schedule can be converted to one that is serial, the schedule is *serializable*
      -  *guarantees consistency!*
   -  not serializable means MAY be inconsistent (not ALWAYS inconsistent)
   -  ![](assets/2024-03-17-19-20-56.png)
   -  ![](assets/2024-03-17-19-22-01.png)
-  **Precendence Graph**
   -  ![](assets/2024-03-17-19-28-01.png)
   -  ![](assets/2024-03-17-19-31-13.png)
   -  ![](assets/2024-03-17-19-31-22.png)


### Isolation Levels
- decreasing isolation will decrease consistency, but increase concurrency
- 4 isolation levels from strongest to weakest:
- **Serializable**
  - little concurrency => poor performance, max consistency
  - must be equivalent in result to a serial schedule
- **Repeatable Read**
  - if $T_i$ reads X, it puts a lock on it so no other transaction $T_j$ can update it
  - requires a lot of locking
  - this is the default in MySQL
- **Read Committed**
  - $T_i$ can *only* read data from another transaction $T_j$ that has already committed it
  - the default in all other RMDBS
- **Read Uncommitted**
  - $T_i$ can read data from *any* other transaction even if it's not committed
- problems:
  - dirty write
    - T1 updates a value and then T2 changes the value before T1 commits
    - cannot ever happen under any isolation level
  - dirty read
    - transaction can read uncommitted changes (from shared memory buffer) from other transactions
    - only the *read uncommitted* iso level allows this
    - ![](assets/2024-03-17-19-49-11.png)
  - fuzzy read / non-repeatable read
    - occurs when T1 reads a value, then T2 updates the value and commits, then T1 reads the value but sees a different one than before
    - only occurs in *read uncommitted* and *read committed* modes
    - ![](assets/2024-03-17-19-52-27.png)
  - phantom read / phantom phenomenon
    - occurs when T2 *inserts or deletes* rows on a table in between two SELECTS of T1
      - only applies to a set of records, not just one record
    - can happen in *read uncommitted*, *read committed*, and *repeatable read*
    - ![](assets/2024-03-17-19-56-30.png)
  - ![](assets/2024-03-17-19-58-33.png)

### Locking for Isolation
- most common way of ensuring consistency under concurrency
  - e.g. repeatable read will put lock on data so that no other transaction can modify it during read
- *shared lock* - allows read access
  - multiple transactions can hold shared locks on a single record X
  - must wait for all shared locks to be released if you want to write
- *exclusive lock* - allows read/write access
  - no other transactions can update (will block instead)
- *starvation*
  - ![](assets/2024-03-18-22-41-54.png)
  - ![](assets/2024-03-18-22-43-07.png)
  - transaction only gets lock to an item if there are no locks on it, or there are no other requests for a lock on it
    - otherwise transaction will block

### Two-Phase Locking (2PL)
- ![](assets/2024-03-18-22-59-05.png)
- each transaction pulls locks on data it needs => no other transaction can modify those values

### Deadlocks
- ![](assets/2024-03-18-23-04-55.png)
- ![](assets/2024-03-18-23-08-26.png)

### Lock Manager
- receives lock/unlock requests and returns either a grant for a lock or an indicator to block
  - unlock request usually returns just ACK, but sometimes has side effect of granting another lock request
- lock requests stored in hash table called *lock table*
  - key is data value, points to link list of transactions that are waiting for lock
- lock manager can *prevent* deadlocks
  - detects deadlocks that are about to occor using a wait-for graph
    - tells the transaction to rollback
- approaches to prevent deadlocks:
  - ![](assets/2024-03-18-23-15-57.png)
- detection of and recovery from deadlocks
  - ![](assets/2024-03-18-23-18-48.png)

### Summary
- ![](assets/2024-03-18-23-24-19.png)

### Transactions in NoSQL
- **Redis**
  - ![](assets/2024-03-18-23-27-43.png)
  - WATCH keys to basically lock them
  - ![](assets/2024-03-18-23-29-05.png)
  - ![](assets/2024-03-18-23-29-14.png)
- **MongoDB**
  - ![](assets/2024-03-18-23-30-08.png)
  - ![](assets/2024-03-18-23-30-29.png)
- **neo4j**
  - ![](assets/2024-03-18-23-31-16.png)

### Summary of Class
- ![](assets/2024-03-19-00-09-00.png)
- ![](assets/2024-03-19-00-10-58.png)
- ![](assets/2024-03-19-00-11-24.png)
- ![](assets/2024-03-19-00-12-06.png)
- ![](assets/2024-03-19-00-13-39.png)