package com.example.demo.Claims;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping; // ¡Añade esta importación!

@RestController
@RequestMapping("/api/claims") // Ruta base para este controlador
public class ClaimController {

    @Autowired
    private ClaimService claimService;

    @PostMapping
    public ResponseEntity<Claim> createClaim(@RequestBody Claim claim) {
        String claimId = "CL-" + java.time.Year.now().getValue() + "-" + String.format("%04d", (int)(Math.random() * 10000));
        claim.setId(claimId);
        claim.setStatus("pending");
        claim.setCreatedAt(java.time.LocalDateTime.now());

        Claim savedClaim = claimService.saveClaim(claim);

        return new ResponseEntity<>(savedClaim, HttpStatus.CREATED);
    }

}