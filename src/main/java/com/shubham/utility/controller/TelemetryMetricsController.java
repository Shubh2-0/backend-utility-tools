package com.shubham.utility.controller;

import com.shubham.utility.dto.TelemetryReportDTO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.lang.management.ManagementFactory;

@RestController
@RequestMapping("/api/v1/telemetry")
@Tag(name = "Telemetry & Metrics", description = "JVM runtime statistics, memory telemetry, and system diagnostics")
public class TelemetryMetricsController {

    @GetMapping("/metrics")
    @Operation(summary = "Get JVM Memory and Thread Telemetry", description = "Retrieves live heap memory allocation, processor count, active threads, and JVM uptime.")
    public ResponseEntity<TelemetryReportDTO> getTelemetryReport() {
        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long maxMemory = runtime.maxMemory();
        int availableProcessors = runtime.availableProcessors();
        int activeThreads = Thread.activeCount();
        double uptimeSeconds = ManagementFactory.getRuntimeMXBean().getUptime() / 1000.0;

        TelemetryReportDTO report = TelemetryReportDTO.builder()
                .status("HEALTHY")
                .timestamp(java.time.LocalDateTime.now())
                .totalMemoryBytes(totalMemory)
                .freeMemoryBytes(freeMemory)
                .maxMemoryBytes(maxMemory)
                .availableProcessors(availableProcessors)
                .activeThreads(activeThreads)
                .jvmUptimeSeconds(uptimeSeconds)
                .environment("PRODUCTION")
                .build();

        return ResponseEntity.ok(report);
    }
}
