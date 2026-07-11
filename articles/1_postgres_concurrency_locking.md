title: Concurrency Control in Financial Ledgers: Pessimistic vs Optimistic Locking
tags: springboot, postgresql, database, java

When building a high-throughput financial ledger like a digital wallet api, concurrency is the biggest silent killer. If two threads attempt to update the same account balance at the exact same millisecond, you risk duplicate spend or inconsistent ledger entries. 

In Java Spring Boot, we typically choose between two main locking strategies: Optimistic and Pessimistic.

### 1. Optimistic Locking (Using @Version)
Optimistic locking assumes conflicts are rare. It uses a version column in the database. When a transaction commits, it checks if the version has changed.
```java
@Entity
public class Account {
    @Id
    private Long id;
    private BigDecimal balance;
    @Version
    private Long version;
}
```
*   **How it works:** Spring Boot executes `UPDATE account SET balance = ?, version = version + 1 WHERE id = ? AND version = ?`.
*   **The Catch:** If another thread updated it first, the version mismatch throws an `OptimisticLockingFailureException`. The application must handle this by retrying the transaction, which adds latency.

### 2. Pessimistic Locking (SELECT ... FOR UPDATE)
Pessimistic locking assumes conflicts are highly likely. It explicitly locks the database row at the beginning of the transaction, blocking any other write operations on that row.
```java
@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Optional<Account> findByIdForUpdate(Long id);
}
```
*   **How it works:** Spring Boot translates this to `SELECT * FROM account WHERE id = ? FOR UPDATE`.
*   **The Catch:** Other threads attempting to read or write this row are blocked until the locking transaction commits or rolls back. This prevents optimistic exceptions but requires careful connection pool tuning to avoid thread starvation.

For low-latency wallet services where balances are frequently updated, pessimistic locking is the safest default to prevent double spend.
