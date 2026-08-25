# Service Discovery with Eureka and Spring Cloud: A Production Hands-On Guide

When you scale beyond two microservices, hardcoding IP addresses or domain names in `application.properties` breaks down fast. Instances get destroyed, auto-scaled up or redeployed on new port allocations. If your payment service has to track where three instances of the order service live, you end up writing custom routing scripts or risking downtime every time a deployment finishes.

In this guide we will set up a production-ready Service Discovery server using Netflix Eureka and Spring Cloud. I've used this exact pattern in production fintech and e-commerce setups where keeping infrastructure costs under ₹100 per month while processing thousands of requests was non-negotiable.

---

## What is Eureka Service Discovery?

Netflix Eureka acts as a dynamic service registry. Think of it as a phone book for your backend services:
1. **Eureka Server**: The central registry where every running instance registers its hostname, IP and port.
2. **Eureka Clients**: Microservices (like `user-service`, `order-service` or `payment-service`) that register themselves at startup and periodically send heartbeats (every 30 seconds by default) to stay active in the registry.

When `order-service` needs to talk to `user-service`, it asks Eureka for the available live instances of `user-service` and client-side load balances the request using Spring Cloud LoadBalancer.

---

## Step 1: Setting Up the Eureka Registry Server

First let's create a standalone Spring Boot application for our Eureka Server.

### Maven Dependencies (`pom.xml`)

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
</dependency>
```

### Application Class

Enable the server using `@EnableEurekaServer`:

```java
package com.tracker.discovery;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@SpringBootApplication
@EnableEurekaServer
public class DiscoveryServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(DiscoveryServerApplication.class, args);
    }
}
```

### Server Configuration (`application.yml`)

Because this is the central server itself, we tell Eureka not to register with itself:

```yaml
server:
  port: 8761

spring:
  application:
    name: discovery-server

eureka:
  instance:
    hostname: localhost
  client:
    register-with-eureka: false
    fetch-registry: false
    service-url:
      defaultZone: http://${eureka.instance.hostname}:${server.port}/eureka/
  server:
    wait-time-in-ms-when-sync-empty: 0
    response-cache-update-interval-ms: 5000
```

Start the application and open `http://localhost:8761` in your browser. You will see the Netflix Eureka dashboard running live.

---

## Step 2: Registering a Microservice (Eureka Client)

Now let's connect a Spring Boot microservice to register automatically with Eureka on startup.

### Client Dependency (`pom.xml`)

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

### Client Configuration (`application.yml`)

```yaml
server:
  port: 8081

spring:
  application:
    name: activity-service

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    registry-fetch-interval-seconds: 5
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 10
    lease-expiration-duration-in-seconds: 30
```

When `activity-service` starts up, it sends a REST register payload to `http://localhost:8761/eureka/`. Refreshing `http://localhost:8761` will show `ACTIVITY-SERVICE` registered under "Instances currently registered with Eureka".

---

## Step 3: Inter-Service Communication with WebClient & LoadBalancer

Now let's call `activity-service` from another microservice using service names instead of hardcoded IPs.

### WebClient Configuration

```java
package com.tracker.gateway.config;

import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class ClientConfig {

    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}
```

### Making the Call

```java
@Service
public class AnalyticsService {

    private final WebClient.Builder webClientBuilder;

    public AnalyticsService(WebClient.Builder webClientBuilder) {
        this.webClientBuilder = webClientBuilder;
    }

    public String fetchUserSummary(String userId) {
        return webClientBuilder.build()
                .get()
                .uri("http://activity-service/api/activitylog/user/{id}", userId)
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}
```

Notice the URL: `http://activity-service/...`. Spring Cloud LoadBalancer automatically resolves `activity-service` to a live IP and port from Eureka's local cache.

---

## Production Gotchas & Best Practices

1. **Eviction Timers & Heartbeats**: Default heartbeat renewal is 30s with a 90s expiration. In fast-restarting cloud deployments, lower `lease-renewal-interval-in-seconds` to 10s and `lease-expiration-duration-in-seconds` to 30s to clean stale instances faster.
2. **Self-Preservation Mode**: If network blips happen, Eureka enters self-preservation mode and stops evicting dead instances to prevent wiping the registry. In local/dev environments set `eureka.server.enable-self-preservation: false`.
3. **Cost Optimization**: In our e-commerce platform that generated over ₹1L in revenue within 2 months, we ran Eureka Server alongside Spring Cloud Config Server on minimal instances (under ₹100/month hosting), keeping RAM usage below 250MB with tuned JVM heap limits (`-Xmx256m`).

---

## Conclusion

Eureka service discovery removes hardcoded networking from microservices architecture. Combined with Spring Cloud Gateway and LoadBalancer, you get instant service registry, health-checking and dynamic routing out of the box.
