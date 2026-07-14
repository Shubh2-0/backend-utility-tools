![Spring Boot Async Completablefuture](https://source.unsplash.com/1200x630/?async,programming,java&sig=1)

> _Published 2026-06-11 by [Shubham Bhati](https://shubh2-0.github.io) — Backend Engineer (Java 17, Spring Boot, Microservices)._

We've all been there - stuck with a slow-performing API endpoint that's causing our application to grind to a halt. In our production environment, we recently encountered an issue where a single endpoint was taking up to 800ms to respond, causing our p99 latency to skyrocket. After some digging, we discovered that the culprit was a synchronous call to an external service. By switching to asynchronous programming using Spring Boot and `CompletableFuture`, we were able to reduce our p99 latency from 800ms to 120ms. This experience taught us the importance of using `spring boot async CompletableFuture` to write non-blocking code.

* [Introduction to Asynchronous Programming](#introduction-to-asynchronous-programming)
* [Using the `@Async` Annotation](#using-the-async-annotation)
* [Working with `CompletableFuture`](#working-with-completablefuture)
* [Configuring Thread Pools](#configuring-thread-pools)
* [Handling Errors and Exceptions](#handling-errors-and-exceptions)
* [Common Mistakes](#common-mistakes)
* [FAQ](#faq)
* [Conclusion](#conclusion)

## Introduction to Asynchronous Programming
Asynchronous programming is a technique that allows our application to perform multiple tasks concurrently, improving overall performance and responsiveness. In Java, we can use the `java.util.concurrent` package to write asynchronous code. Spring Boot provides additional support for asynchronous programming through the `@Async` annotation and `CompletableFuture`. By using these tools, we can write non-blocking code that's easier to maintain and scales better.

## Using the `@Async` Annotation
The `@Async` annotation is a convenient way to mark a method as asynchronous. When we annotate a method with `@Async`, Spring Boot will automatically execute it in a separate thread. Here's an example:
```java
@Service
public class MyService {
 
    @Async
    public CompletableFuture<String> doSomethingAsync() {
        // Simulate some long-running operation
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return CompletableFuture.completedFuture("Done");
    }
}
```
In this example, the `doSomethingAsync` method is annotated with `@Async`, indicating that it should be executed asynchronously.

## Working with `CompletableFuture`
`CompletableFuture` is a powerful tool for working with asynchronous operations. It provides a flexible way to compose and combine multiple asynchronous tasks. Here's an example:
```java
public CompletableFuture<String> doSomethingAsync() {
    CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
        // Simulate some long-running operation
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Done";
    });
    return future;
}
```
In this example, we use `CompletableFuture.supplyAsync` to create a new `CompletableFuture` instance that represents an asynchronous operation.

## Configuring Thread Pools
When working with asynchronous programming, it's essential to configure thread pools properly. By default, Spring Boot uses a single thread pool with a fixed size of 10 threads. However, we can customize this behavior by creating a custom thread pool configuration. Here's an example:
```java
@Configuration
public class ThreadPoolConfig {
 
    @Bean
    public TaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("my-thread-");
        executor.initialize();
        return executor;
    }
}
```
In this example, we create a custom thread pool configuration with a core pool size of 10 threads and a maximum pool size of 20 threads.

## Handling Errors and Exceptions
When working with asynchronous programming, it's crucial to handle errors and exceptions properly. We can use `try-catch` blocks to catch and handle exceptions, but we can also use `CompletableFuture.exceptionally` to handle exceptions in a more elegant way. Here's an example:
```java
public CompletableFuture<String> doSomethingAsync() {
    CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
        // Simulate some long-running operation
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Done";
    });
    return future.exceptionally(ex -> {
        // Handle the exception
        return "Error";
    });
}
```
In this example, we use `CompletableFuture.exceptionally` to handle exceptions in a more elegant way.

## Handling Cancellation
When working with asynchronous programming, it's essential to handle cancellation properly. We can use `CompletableFuture.cancel` to cancel an ongoing asynchronous operation. Here's an example:
```java
public CompletableFuture<String> doSomethingAsync() {
    CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
        // Simulate some long-running operation
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Done";
    });
    // Cancel the operation
    future.cancel(true);
    return future;
}
```
In this example, we use `CompletableFuture.cancel` to cancel an ongoing asynchronous operation.

## Common Mistakes
Here are some common mistakes to avoid when working with asynchronous programming:
* Not using `@Async` annotation correctly
* Not configuring thread pools properly
* Not handling errors and exceptions correctly
* Not using `CompletableFuture` correctly
* Not testing asynchronous code thoroughly

## FAQ
### What is the difference between `@Async` and `CompletableFuture`?
`@Async` is an annotation that marks a method as asynchronous, while `CompletableFuture` is a class that represents an asynchronous operation. We can use `@Async` to mark a method as asynchronous, and then use `CompletableFuture` to work with the resulting asynchronous operation.

### How do I configure thread pools in Spring Boot?
We can configure thread pools in Spring Boot by creating a custom thread pool configuration using the `ThreadPoolTaskExecutor` class. We can also use the `@Bean` annotation to define a custom thread pool configuration.

### What is the best way to handle errors and exceptions in asynchronous programming?
The best way to handle errors and exceptions in asynchronous programming is to use `try-catch` blocks to catch and handle exceptions, and then use `CompletableFuture.exceptionally` to handle exceptions in a more elegant way.

### How do I test asynchronous code?
We can test asynchronous code by using testing frameworks such as JUnit or TestNG, and then using mock objects to simulate asynchronous operations. We can also use tools such as [Spring Boot Test](https://docs.spring.io/spring-boot/docs/current/reference/html/spring-boot-features.html#boot-features-testing) to test asynchronous code.

## Conclusion
In conclusion, asynchronous programming is a powerful technique that can improve the performance and responsiveness of our application. By using `spring boot async CompletableFuture`, we can write non-blocking code that's easier to maintain and scales better. We can also use `@Async` annotation and `CompletableFuture` to work with asynchronous operations, and then configure thread pools and handle errors and exceptions correctly. For more information, we can refer to the [Spring Boot documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/spring-boot-features.html#boot-features-async) or the [Java documentation](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html).

---

![Spring Boot Async Completablefuture in production](https://source.unsplash.com/1000x500/?async,programming,java&sig=2)

## Further Reading

- [Spring Boot Official Documentation](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Baeldung — Java & Spring Tutorials](https://www.baeldung.com/)
- [Oracle Java Documentation](https://docs.oracle.com/en/java/)

---

*Written by **Shubham Bhati** — Backend Engineer at AlignBits LLC, specializing in Java 17, Spring Boot, microservices, and AI integration. Connect on [LinkedIn](https://linkedin.com/in/bhatishubham), [GitHub](https://github.com/Shubh2-0), or read more at [shubh2-0.github.io](https://shubh2-0.github.io).*
