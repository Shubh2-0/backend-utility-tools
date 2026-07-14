package com.shubham.utility.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TelemetryReportDTO {
    private String status;
    private LocalDateTime timestamp;
    private long totalMemoryBytes;
    private long freeMemoryBytes;
    private long maxMemoryBytes;
    private int availableProcessors;
    private int activeThreads;
    private double jvmUptimeSeconds;
    private String environment;
}
