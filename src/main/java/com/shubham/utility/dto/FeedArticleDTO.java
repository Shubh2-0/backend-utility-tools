package com.shubham.utility.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FeedArticleDTO {
    private String id;
    private String title;
    private String link;
    private String category;
    private String publishDate;
    private String author;
}
