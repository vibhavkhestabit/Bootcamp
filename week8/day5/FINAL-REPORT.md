# Capstone Engineering Report: Local LLM Microservice Deployment

## 1. Architectural Foundation: Framework Selection

The primary objective of this capstone was to transition the AI from an isolated, local terminal script into a deployable, standalone backend microservice.
**The FastAPI Engine:** FastAPI was selected as the core framework due to its modern, asynchronous Python architecture. Instead of relying on manual terminal inputs, the LLM is now exposed to a network port (localhost:8000), allowing it to actively listen for and process HTTP requests from external applications, frontends, or other microservices.

## 2. Memory Management: Model Caching Strategy

- Loading a .gguf file from disk to memory is a computationally heavy process that takes several seconds. Performing this operation on every API call would create unacceptable bottlenecks.
- **The Singleton Pattern:** The architecture implements a strict model caching strategy. The LLM is loaded into System RAM exactly once during the initial server startup. It remains "warm" in memory, dropping the response latency to near-zero for all subsequent network requests.

## 3. Deployment Readiness: Configuration Management

Hardcoding absolute paths, memory limits, and generation variables directly into API endpoints is an anti-pattern that breaks when moving code between development, UAT, and production environments.

**Centralized Configuration:** All environmental settings (such as file paths, max token limits, and default temperatures) are abstracted into a dedicated configuration file. This makes the application highly modular, easily maintainable, and strictly ready for containerization and deployment.

## 4. API Specification: Single-Turn Generation (POST /generate)

The microservice exposes two distinct REST API endpoints to serve entirely different application needs.
Standard Completion: The /generate endpoint takes a single, raw text string and processes it. It is strictly designed for stateless, one-off tasks where memory is not required, such as text summarization, code snippet generation, or auto-complete integrations.

## 5. API Specification: Multi-Turn Conversation & RAG (POST /chat)

The /chat endpoint is a highly structured interface that requires an array of messages categorized by specific roles (system, user, assistant).
1) **Infinite Chat Mode:** By accepting an array, a frontend application can continuously pass the entire conversation history back to the server. This simulates AI "memory," allowing it to maintain context up to its maximum 2048 token limit.
2) **RAG & Agent Readiness:** Because this endpoint strictly isolates and parses system prompts, it serves as the perfect foundational engine for Retrieval-Augmented Generation (RAG). It is structurally ready to accept massive blocks of context retrieved from vector databases or hybrid text-image searches, silently injecting that context into the system prompt before addressing the user.

## 6. Latency Optimization: Token Streaming

Waiting for an LLM to generate an entire 500-word response in memory before returning the HTTP request creates massive perceived latency for the end-user.
**Streamed Generations:** To solve this, the API utilizes streaming protocols. The server yields chunks of text over the network exactly token-by-token as they are calculated by the CPU. This drastically reduces the time-to-first-token and provides a real-time, ChatGPT-like experience.

## 7. Generation Controls: Inference Tuning

To ensure the API is flexible for different use cases, both endpoints expose advanced generation controls to the client application:
- **Temperature:** Acts as a creativity dial. Setting it low (0.1) forces the AI to be highly analytical and strictly predictable, while setting it high (0.9) encourages creative and chaotic outputs.
- **Top-K & Top-P Sampling:** These are strict mathematical guardrails placed on the AI's vocabulary pool during generation. By limiting the probability distribution of the next predicted token, the API prevents the AI from hallucinating or choosing nonsensical words when operating at higher temperatures.

## Output

![ss](screenshots/ss1.png)
![ss](screenshots/ss2.png)
![ss](screenshots/ss3.png)