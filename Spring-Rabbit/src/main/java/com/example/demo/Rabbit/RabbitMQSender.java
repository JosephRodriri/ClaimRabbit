package com.example.demo.Rabbit;

import com.example.demo.Claims.Claim;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class RabbitMQSender {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.exchange.name}")
    private String exchange;

    @Value("${rabbitmq.routing.key.claim.created}")
    private String routingKeyClaimCreated;

    @Value("${rabbitmq.routing.key.claim.updated}")
    private String routingKeyClaimUpdated;

    public void sendClaimCreatedEvent(Claim claim) {
        rabbitTemplate.convertAndSend(exchange, routingKeyClaimCreated, claim);
        System.out.println("Claim Created Event Sent: " + claim.getId());
    }
    public void sendClaimUpdatedEvent(Claim claim) {
        rabbitTemplate.convertAndSend(exchange, routingKeyClaimUpdated, claim);
        System.out.println("Claim Updated Event Sent: " + claim.getId());
    }
}
