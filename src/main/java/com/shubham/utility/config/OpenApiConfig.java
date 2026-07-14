package com.shubham.utility.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Backend Utility & Telemetry Suite API")
                        .version("1.0.0")
                        .description("Production-grade Java 17 & Spring Boot 3 utility engine providing RSS feed aggregation, JVM telemetry metrics, and API health monitoring.")
                        .contact(new Contact()
                                .name("Shubham Bhati")
                                .email("shubhambhati226@gmail.com")
                                .url("https://github.com/Shubh2-0"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")));
    }
}
