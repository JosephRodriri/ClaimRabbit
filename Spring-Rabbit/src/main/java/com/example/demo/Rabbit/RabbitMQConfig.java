package com.example.demo.Rabbit; // Paquete de RabbitMQConfig

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    // Estas constantes se usarán para los nombres del exchange y las routing keys
    // Asegúrate de que coincidan con los de application.properties
    public static final String CLAIMS_EXCHANGE = "claims_exchange";
    public static final String CLAIMS_CREATED_QUEUE = "claims_created_queue";
    public static final String CLAIMS_CREATED_ROUTING_KEY = "claims.created";
    public static final String CLAIMS_UPDATED_QUEUE = "claims_updated_queue";
    public static final String CLAIMS_UPDATED_ROUTING_KEY = "claims.updated";


    @Bean
    public TopicExchange claimsExchange() {
        // Declara el exchange como un bean de Spring
        return new TopicExchange(CLAIMS_EXCHANGE);
    }

    @Bean
    public Queue claimsCreatedQueue() {
        // Declara la cola para los reclamos creados
        return new Queue(CLAIMS_CREATED_QUEUE, true); // 'true' significa que la cola es durable
    }

    @Bean
    public Binding bindingCreatedClaim() {
        // Enlaza la cola 'claimsCreatedQueue' al 'claimsExchange' usando la routing key 'claims.created'
        return BindingBuilder.bind(claimsCreatedQueue())
                .to(claimsExchange())
                .with(CLAIMS_CREATED_ROUTING_KEY);
    }

    @Bean
    public Queue claimsUpdatedQueue() {
        // Declara la cola para los reclamos actualizados
        return new Queue(CLAIMS_UPDATED_QUEUE, true);
    }

    @Bean
    public Binding bindingUpdatedClaim() {
        // Enlaza la cola 'claimsUpdatedQueue' al 'claimsExchange' usando la routing key 'claims.updated'
        return BindingBuilder.bind(claimsUpdatedQueue())
                .to(claimsExchange())
                .with(CLAIMS_UPDATED_ROUTING_KEY);
    }
}