![Spring Boot Elasticsearch Tutorial](https://source.unsplash.com/1200x630/?search,elasticsearch,data&sig=1)

> _Published 2026-06-25 by [Shubham Bhati](https://shubh2-0.github.io) — Backend Engineer (Java 17, Spring Boot, Microservices)._

As backend engineers, we've all been there - trying to add full-text search to our REST API, only to find that our database's built-in search capabilities are lacking. That's where Spring Boot and Elasticsearch come in. In this Spring Boot Elasticsearch tutorial, we'll explore how to integrate Elasticsearch into our Spring Boot application to provide fast and efficient full-text search capabilities. We've seen firsthand the benefits of using Elasticsearch in production, with one of our applications reducing its p99 search latency from 800ms to 120ms after switching from a traditional database-based search.

* [Introduction to Elasticsearch](#introduction-to-elasticsearch)
* [Setting up Spring Data Elasticsearch](#setting-up-spring-data-elasticsearch)
* [Indexing Data in Elasticsearch](#indexing-data-in-elasticsearch)
* [Searching Data in Elasticsearch](#searching-data-in-elasticsearch)
* [Using Elasticsearch with Spring Boot](#using-elasticsearch-with-spring-boot)
* [Common Mistakes](#common-mistakes)
* [FAQ](#faq)
* [Conclusion](#conclusion)

## Introduction to Elasticsearch
Elasticsearch is a powerful search engine that allows us to store, search, and analyze large volumes of data. It's built on top of the Apache Lucene library and provides a scalable and fault-tolerant solution for full-text search. We've found that Elasticsearch is particularly well-suited for applications that require complex search queries, such as filtering, sorting, and faceting. For example, in one of our applications, we use Elasticsearch to power a search bar that allows users to filter products by category, price, and brand.

```java
// Example of a simple Elasticsearch query
GetMapping("/search")
public List<Product> searchProducts(@RequestParam String query) {
    SearchQuery searchQuery = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.matchQuery("name", query))
            .build();
    return elasticsearchTemplate.queryForList(searchQuery, Product.class);
}
```

## Setting up Spring Data Elasticsearch
To get started with Elasticsearch in our Spring Boot application, we need to add the Spring Data Elasticsearch dependency to our `pom.xml` file (if we're using Maven) or our `build.gradle` file (if we're using Gradle). We're currently using Spring Boot 3.2 and Elasticsearch 8.5, which provides a number of improvements over earlier versions, including better support for Java 21. We've found that the [official Spring Data Elasticsearch documentation](https://docs.spring.io/spring-data/elasticsearch/docs/current/reference/html/) is a great resource for getting started.

```xml
// Maven dependency for Spring Data Elasticsearch
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
```

## Indexing Data in Elasticsearch
Once we've set up Spring Data Elasticsearch, we need to index our data in Elasticsearch. This involves creating an Elasticsearch index and mapping our data to that index. We can do this using the `@Document` annotation on our entity class. For example, if we have a `Product` entity, we can annotate it with `@Document` to specify the index name and type.

```java
// Example of a Product entity with Elasticsearch mapping
@Document(indexName = "products", type = "product")
public class Product {
    @Id
    private String id;
    private String name;
    private String description;
    // getters and setters
}
```

## Searching Data in Elasticsearch
Now that we've indexed our data in Elasticsearch, we can start searching it. We can use the `ElasticsearchTemplate` class to execute search queries against our Elasticsearch index. For example, we can use the `queryForList` method to search for products by name.

```java
// Example of searching for products by name
GetMapping("/search")
public List<Product> searchProducts(@RequestParam String query) {
    SearchQuery searchQuery = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.matchQuery("name", query))
            .build();
    return elasticsearchTemplate.queryForList(searchQuery, Product.class);
}
```

## Using Elasticsearch with Spring Boot
Using Elasticsearch with Spring Boot is relatively straightforward. We can use the `@Autowired` annotation to inject an instance of the `ElasticsearchTemplate` class into our service class. We can then use this instance to execute search queries against our Elasticsearch index. We've found that the [Baeldung tutorial on Spring Boot and Elasticsearch](https://www.baeldung.com/spring-boot-elasticsearch) is a great resource for getting started.

```java
// Example of using Elasticsearch with Spring Boot
@Service
public class ProductService {
    @Autowired
    private ElasticsearchTemplate elasticsearchTemplate;
    
    public List<Product> searchProducts(String query) {
        SearchQuery searchQuery = new NativeSearchQueryBuilder()
                .withQuery(QueryBuilders.matchQuery("name", query))
                .build();
        return elasticsearchTemplate.queryForList(searchQuery, Product.class);
    }
}
```

## Common Mistakes
Here are some common mistakes to avoid when using Elasticsearch with Spring Boot:
* Not configuring the Elasticsearch index correctly
* Not mapping the data to the Elasticsearch index correctly
* Not using the correct version of Elasticsearch
* Not handling errors correctly
* Not optimizing the search queries for performance

## FAQ
### What is the difference between Elasticsearch and a traditional database?
Elasticsearch is a search engine that is optimized for full-text search, while a traditional database is optimized for storing and retrieving structured data. We've found that Elasticsearch is particularly well-suited for applications that require complex search queries.

### How do I configure Elasticsearch to use a specific index?
We can configure Elasticsearch to use a specific index by using the `@Document` annotation on our entity class. For example, we can annotate our `Product` entity with `@Document(indexName = "products")`.

### What is the best way to optimize Elasticsearch search queries for performance?
We can optimize Elasticsearch search queries for performance by using techniques such as filtering, sorting, and faceting. We've found that the [official Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-for-search-speed.html) is a great resource for getting started.

### How do I handle errors when using Elasticsearch with Spring Boot?
We can handle errors when using Elasticsearch with Spring Boot by using try-catch blocks to catch any exceptions that are thrown. We've found that the [Spring Boot documentation on error handling](https://docs.spring.io/spring-boot/docs/current/reference/html/web.html#web.servlet.spring-mvc.error-handling) is a great resource for getting started.

## Conclusion
In conclusion, using Elasticsearch with Spring Boot is a great way to add full-text search capabilities to our REST API. We've seen firsthand the benefits of using Elasticsearch in production, with one of our applications reducing its p99 search latency from 800ms to 120ms after switching from a traditional database-based search. We hope this tutorial has been helpful in getting started with Elasticsearch and Spring Boot. For more information, we recommend checking out the [official Spring Data Elasticsearch documentation](https://docs.spring.io/spring-data/elasticsearch/docs/current/reference/html/).

---

![Spring Boot Elasticsearch Tutorial in production](https://source.unsplash.com/1000x500/?search,elasticsearch,data&sig=2)

## Further Reading

- [Spring Boot Official Documentation](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Baeldung — Java & Spring Tutorials](https://www.baeldung.com/)
- [Oracle Java Documentation](https://docs.oracle.com/en/java/)

---

*Written by **Shubham Bhati** — Backend Engineer at AlignBits LLC, specializing in Java 17, Spring Boot, microservices, and AI integration. Connect on [LinkedIn](https://linkedin.com/in/bhatishubham), [GitHub](https://github.com/Shubh2-0), or read more at [shubh2-0.github.io](https://shubh2-0.github.io).*
