# OpenAI in Production: A Java Backend Engineer's Field Notes

*By Shubham Bhati — Backend Engineer at AlignBits LLC*

---

Most "OpenAI tutorials" stop at a hello-world chat call. This isn't that. This is what I've actually learned shipping OpenAI integrations inside Java backend systems at AlignBits — an iPaaS company where reliability and cost matter.

If you're a Java backend engineer about to wire OpenAI into a Spring Boot service, here's what you actually need to know.

---

## 1. The OpenAI Java SDK situation

OpenAI doesn't ship an official Java SDK (as of writing). Your options:

**Option A — Spring AI** (recommended)
- Maven coords: `org.springframework.ai:spring-ai-openai-spring-boot-starter`
- Idiomatic Spring Boot, supports multiple LLMs (OpenAI, Anthropic, Gemini), good test support
- Best for new Spring Boot projects

**Option B — Community SDKs**
- `com.theokanning.openai-gpt3-java` is the most mature community SDK
- More features, but doesn't follow Spring conventions

**Option C — Raw HTTP with WebClient or OkHttp**
- Maximum control, minimum dependencies
- Good if you only call 1-2 endpoints

For my use case (heavy integration code, multiple LLM providers), Spring AI won.

---

## 2. The cost problem nobody warns you about

Your first instinct will be: "use GPT-4 for everything, it's smartest." Your CFO will hate you.

**What actually works in production:**
- Use the cheapest model that passes your evals. GPT-4o-mini handles 80% of classification/extraction tasks.
- Cache responses for identical prompts (Redis works fine).
- Use **prompt caching** when supported — Anthropic's caching is automatic but for OpenAI you control it via the cache_control field.
- Truncate long inputs intelligently. Don't ship the whole document if you only need 3 paragraphs.

In my pipelines, prompt caching alone cut LLM costs by 40%.

---

## 3. Reliability: this is an unreliable dependency

Production rule #1: OpenAI is a slow, sometimes-failing remote service. Treat it like any flaky third-party API.

**What every OpenAI integration needs:**

```java
@Component
public class OpenAIService {

    private final OpenAiChatClient chatClient;
    private final RetryTemplate retryTemplate;
    private final CircuitBreaker circuitBreaker;

    public String classify(String input) {
        return circuitBreaker.executeSupplier(() ->
            retryTemplate.execute(ctx -> {
                ChatResponse response = chatClient.call(
                    new Prompt(input,
                        OpenAiChatOptions.builder()
                            .withTimeout(Duration.ofSeconds(30))
                            .withMaxTokens(200)
                            .build())
                );
                return response.getResult().getOutput().getContent();
            })
        );
    }
}
```

The non-negotiables:
- **Timeout** — without it, your thread pool eventually starves on slow OpenAI responses
- **Retry with exponential backoff** — for 429 and 503
- **Circuit breaker** — Resilience4j; trips when error rate >50% over 1 minute
- **Bounded queue** — never let request volume become unbounded

---

## 4. Async or sync?

The temptation is to call OpenAI from your main request thread. Don't.

In Spring Boot, push every OpenAI call onto:
- A bounded `@Async` executor with sensible queue + reject policy, OR
- A message queue (RabbitMQ / SQS) where a separate consumer handles AI calls

Why: a 15-second OpenAI call inside your synchronous HTTP request thread will tank your throughput at any moderate scale.

At AlignBits, we route AI calls through RabbitMQ. Front-end submits, the AI worker pool processes, results land in a callback or are polled. Your p99 latency stops depending on OpenAI's mood.

---

## 5. Output reliability — JSON mode is your friend

The single biggest production headache with LLMs is parse-failures. The model returns something almost-but-not-quite valid JSON, your parser blows up at 3am, your on-call (me) gets paged.

Two fixes that actually work:
- Use **JSON mode** / structured output when the API supports it
- Use **JSON schema** to constrain the response shape

In Spring AI:
```java
ChatResponse response = chatClient.call(
    new Prompt(input,
        OpenAiChatOptions.builder()
            .withResponseFormat(new ResponseFormat("json_object"))
            .build())
);
```

Then validate the JSON against your schema **before** mapping to your domain object. Failures = retry once with a more specific prompt, then dead-letter.

---

## 6. Logging without leaking PII

Healthcare backends taught me this the hard way at IHX. You will be tempted to log full prompts + completions for debugging. Don't, if your input contains anything sensitive.

**Pattern that works:**
- Hash the input → log the hash, not the content
- Log token counts, model, latency, finish reason
- For successful calls, log nothing about the content
- For failed calls, store the prompt+response in a separate audit table with TTL

```java
log.info("openai.call model={} input_hash={} input_tokens={} output_tokens={} latency_ms={} finish_reason={}",
    model, inputHash, inputTokens, outputTokens, latencyMs, finishReason);
```

---

## 7. Testing OpenAI-integrated code

You can't hit the live API in CI. You'd burn money and tests would be flaky.

**The pattern I use:**
- Wrap the LLM call in an interface `LLMClient`
- Have `OpenAIClient` (prod) and `MockLLMClient` (test)
- Tests inject the mock; record realistic responses for golden-path tests
- Run a **separate** "live integration" job nightly that hits OpenAI in a staging key and alerts on contract changes

This catches prompt drift before customers do.

---

## 8. Prompts are code. Version them.

A prompt change is a deploy. Treat it like code:
- Prompts live in your repo, not in OpenAI's playground
- Each prompt has a version number
- Changes go through code review
- You can roll back

I keep prompts in `src/main/resources/prompts/` as `.txt` files with a header:
```
# id: classify-invoice-v3
# author: shubham.bhati
# changed: 2026-04-12
# purpose: extracts vendor + amount + due date from invoice text
...
```

---

## The bottom line

OpenAI in production isn't `chatClient.call("hello")`. It's:
- A queue
- A circuit breaker
- A retry policy
- A cost model
- A version-controlled prompt library
- A redacted log pipeline

If you've shipped any other third-party integration, you know this pattern. Don't let "AI" make you forget your engineering instincts.

---

*Shubham Bhati is a Backend Engineer at MobilePe Fintech building Java + Spring Boot integration pipelines in production. Based in Noida, India. [Portfolio](https://shubh2-0.github.io) · [GitHub](https://github.com/Shubh2-0) · [LinkedIn](https://linkedin.com/in/bhatishubham)*

---

**Publishing checklist:**
- [ ] Cover image: a system architecture diagram (request → queue → AI worker → DB)
- [ ] Tags: `#java` `#springboot` `#openai` `#ai` `#backend` `#microservices` `#productionsoftware` `#javadevelopment`
- [ ] Cross-post to Dev.to + Hashnode after 24h (Medium first for canonical)
- [ ] Pin tweet linking to this post
