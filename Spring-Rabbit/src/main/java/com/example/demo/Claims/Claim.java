package com.example.demo.Claims;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

@Document(collection = "claims")
@NoArgsConstructor
@Data
@AllArgsConstructor
public class Claim {
    @Id
    private String id;
    private String policyNumber;
    private String clientId;
    private String clientName;
    private String type;
    private String description;
    private String location;
    private String contactPhone;
    private String date;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
