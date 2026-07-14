title: Preventing Database Meltdowns: Caching Strategies That Actually Work
tags: springboot, redis, systemdesign, java

When scaling a high-throughput backend, the database is always your primary bottleneck. Every network roundtrip to fetch static or semi-static data wastes CPU cycles and spikes connection pool latency. 

To prevent database meltdowns, we implement distributed caching using Redis. But simply throwing `@Cacheable` on a Spring Boot service method is not enough. You must understand how to manage cache lifecycles.

Here are three production-tested strategies we use to keep systems highly resilient.

### 1. The Cache-Aside Pattern
This is the most common caching pattern. The application code orchestrates both the cache and the database.
```java
public Account getAccountBalance(Long id) {
    String cacheKey = "account:" + id;
    Account account = redisTemplate.opsForValue().get(cacheKey);
    
    if (account != null) {
        return account; // Cache Hit
    }
    
    // Cache Miss
    account = accountRepository.findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Account not found"));
        
    redisTemplate.opsForValue().set(cacheKey, account, Duration.ofMinutes(15));
    return account;
}
```
*   **The Catch:** You must ensure cache eviction happens whenever data changes (e.g. during updates) to prevent serving stale data.

### 2. Guarding Against Cache Penetration (Bloom Filters)
Cache penetration occurs when requests query keys that do not exist in either the cache or the database. If malicious actors flood your API with random IDs, every single request bypasses the cache and hits the database directly.
*   **The Solution:** Use a **Bloom Filter** in front of your cache. A Bloom Filter is a space-efficient probabilistic data structure that can tell you with 100% certainty if an element is *not* present in the system.
*   If the Bloom Filter says the ID does not exist, reject the request immediately without hitting Redis or the database.

### 3. Tuning Time-To-Live (TTL) & Jitter
Setting a hard TTL (like exactly 1 hour) on all keys can cause a **Cache Stampede**. If 10,000 product keys expire at the exact same second, the next wave of concurrent requests will hit the database at the same time, causing a temporary spike in latency.
*   **The Solution:** Add a small randomized delay (jitter) to your TTL. Instead of 60 minutes, set the expiration to `60 + random(1 to 5) minutes`. This distributes database read operations smoothly over time.

By combining Cache-Aside with Bloom Filters and randomized TTLs, you protect your primary database from unexpected load spikes.
