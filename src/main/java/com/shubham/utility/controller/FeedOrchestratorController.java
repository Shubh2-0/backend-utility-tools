package com.shubham.utility.controller;

import com.shubham.utility.dto.FeedArticleDTO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/feed")
@Tag(name = "RSS & Article Orchestrator", description = "Aggregates technical feed items and developer blog publications")
public class FeedOrchestratorController {

    @GetMapping("/articles")
    @Cacheable("feedArticles")
    @Operation(summary = "Get Consolidated Feed Articles", description = "Returns cached list of aggregated backend development publications and technical articles.")
    public ResponseEntity<List<FeedArticleDTO>> getAggregatedArticles() {
        List<FeedArticleDTO> articles = List.of(
                FeedArticleDTO.builder()
                        .id("art-1")
                        .title("Spring Boot 3.3 & Java 17 Production Optimization Guide")
                        .link("https://shubh2-0.github.io/articles/springboot-performance")
                        .category("Spring Boot")
                        .publishDate("2026-07-14")
                        .author("Shubham Bhati")
                        .build(),
                FeedArticleDTO.builder()
                        .id("art-2")
                        .title("Optimizing PostgreSQL Connection Pools & Lock Contention in High-Throughput Microservices")
                        .link("https://shubh2-0.github.io/articles/postgres-locking")
                        .category("Database Architecture")
                        .publishDate("2026-07-12")
                        .author("Shubham Bhati")
                        .build(),
                FeedArticleDTO.builder()
                        .id("art-3")
                        .title("Event-Driven Microservices: Kafka Partitions & Dead-Letter Queue Strategies")
                        .link("https://shubh2-0.github.io/articles/kafka-dlq-patterns")
                        .category("Apache Kafka")
                        .publishDate("2026-07-10")
                        .author("Shubham Bhati")
                        .build()
        );

        return ResponseEntity.ok(articles);
    }
}
