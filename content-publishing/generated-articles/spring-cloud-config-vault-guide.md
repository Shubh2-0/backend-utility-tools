# Centralized Secret Management with Spring Cloud Config & Vault: A Production Guide

> Subtitle: How to manage environment properties and encrypted database secrets across microservices without rebuilding containers.

Hardcoding DB credentials, JWT secrets or API keys inside `application.yml` or Docker images is a security disaster waiting to happen. Rotating a password shouldn't require rebuilding 10 microservice containers and triggering a full redeployment pipeline.

In Part 2 of our Spring Boot Microservices series, we will build a centralized configuration server using **Spring Cloud Config** integrated with **HashiCorp Vault** for secret encryption.

---

## 🔍 Why Centralized Configuration Management?

In microservices architectures, centralized config management solves three critical challenges:

1. **Zero-Downtime Secret Rotation**: Change database passwords or API keys in Vault without restarting microservices.
2. **Environment Isolation**: Maintain separate profile configurations (`dev`, `staging`, `prod`) in a single Git or Vault backend.
3. **Audit Logging**: Every secret read or modification is logged with timestamps and identity tokens.

---

## 🛠️ Step 1: Setting Up the Spring Cloud Config Server

Create a standalone Spring Boot application for your Config Server.

### Maven Dependencies (`pom.xml`)

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-config-server</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-vault-config</artifactId>
</dependency>
```

### Application Main Class

Enable config server functionality with `@EnableConfigServer`:

```java
package com.tracker.configserver;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

### Server Configuration (`application.yml`)

```yaml
server:
  port: 8888

spring:
  application:
    name: config-server
  profiles:
    active: vault
  cloud:
    vault:
      host: localhost
      port: 8200
      scheme: http
      authentication: TOKEN
      token: s.myProductionVaultTokenSecret
```

---

## 📡 Step 2: Binding Microservice Clients to Config Server

Connect your microservice (`payment-service`) to pull properties dynamically at startup.

### Client Configuration (`application.yml`)

```yaml
spring:
  application:
    name: payment-service
  config:
    import: "configserver:http://localhost:8888"
  profiles:
    active: prod
```

---

## ⚡ Step 3: Dynamic Refresh without Restart (`@RefreshScope`)

Annotate beans that consume dynamic properties with `@RefreshScope`:

```java
package com.tracker.payment.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.stereotype.Component;

@Component
@RefreshScope
public class PaymentGatewayConfig {

    @Value("${payment.stripe.secret-key}")
    private String stripeSecretKey;

    public String getStripeSecretKey() {
        return stripeSecretKey;
    }
}
```

When you update a property in Vault, trigger a POST request to `http://localhost:8082/actuator/refresh` to reload the bean instantly without restarting the container!

---

## 🚀 Production Best Practices

> 💡 **Production Tip**: Centralized config servers can be hosted on minimal 250MB heap RAM instances (costing under ₹100/month) while securing sensitive production microservices.

1. **Vault Lease Renewal**: Set TTLs on Vault database credentials so DB passwords auto-rotate every 24 hours.
2. **Fail-Fast Configuration**: Set `spring.cloud.config.fail-fast: true` so a microservice immediately fails startup if it cannot connect to the Config Server rather than running with missing properties.

---

## 🎯 Summary

Spring Cloud Config and Vault provide production-grade secret management and zero-downtime property updates across distributed microservices.
