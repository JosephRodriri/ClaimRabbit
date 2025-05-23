package com.example.demo.Claims; // Paquete de ClaimService

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.example.demo.Rabbit.RabbitMQConfig; // <--- Esta es la importación correcta para RabbitMQConfig

@Service
public class ClaimService {

    private static final Logger log = LoggerFactory.getLogger(ClaimService.class);

    @Autowired
    private ClaimRepository claimRepository;

    @Autowired
    private RabbitTemplate rabbitTemplate;

    public Claim saveClaim(Claim claim) {
        Claim savedClaim = claimRepository.save(claim); // Guarda el reclamo en MongoDB

        // Lógica para enviar el mensaje a RabbitMQ
        try {
            log.info("Attempting to send message to RabbitMQ. Exchange: {}, Routing Key: {}, Message: {}",
                    RabbitMQConfig.CLAIMS_EXCHANGE, RabbitMQConfig.CLAIMS_CREATED_ROUTING_KEY, savedClaim);
            rabbitTemplate.convertAndSend(RabbitMQConfig.CLAIMS_EXCHANGE,
                    RabbitMQConfig.CLAIMS_CREATED_ROUTING_KEY,
                    savedClaim);
            log.info("Message sent to RabbitMQ successfully for claim ID: {}", savedClaim.getId());
        } catch (Exception e) {
            log.error("Failed to send message to RabbitMQ for claim ID: {}. Error: {}", savedClaim.getId(), e.getMessage(), e);
            // Considera cómo manejar este error (ej. reintentos, dead-letter queue)
        }

        return savedClaim;
    }
}