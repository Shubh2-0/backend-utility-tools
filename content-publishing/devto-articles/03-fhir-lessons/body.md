# 15 Production Incidents in a Healthcare Backend: What FHIR Taught Me About Reliability

*By Shubham Bhati — Backend Engineer at AlignBits LLC*

---

When I joined IHX Private Limited in June 2023 as an Associate Software Engineer, I had Masai's certificate and a few personal Java projects. By the time I left in August 2024, I'd resolved 15+ production incidents on FHIR-standard healthcare backend systems.

That number sounds bad. It isn't. Production engineering is where you actually learn to build software. Here's what FHIR healthcare backends taught me — beyond what any Spring Boot tutorial covers.

---

## What FHIR is (in 60 seconds)

FHIR — **Fast Healthcare Interoperability Resources** — is a standard for exchanging healthcare data. Think of it as REST + JSON for hospitals, labs, insurers, and EHR systems.

Every domain object is a "Resource": `Patient`, `Practitioner`, `Encounter`, `Observation`, `Coverage`, `Claim`. Each has a well-defined JSON schema with strict validation rules.

In Java, the standard library is [HAPI FHIR](https://hapifhir.io/). It's huge, opinionated, and 95% of what you need.

---

## What "production" means in healthcare

In a typical SaaS, an outage costs revenue. In healthcare:

- A patient might not get their meds approved.
- A claim might be misrouted.
- A practitioner might see wrong data.
- Regulators audit your logs.

This isn't fear-mongering. It's why FHIR healthcare backends force you to learn engineering disciplines that consumer apps let you skip.

---

## Lesson 1: Schema validation is not optional

Patient records flow in from ~20 different EHR vendors. Each interprets FHIR slightly differently. Some send dates as `YYYY-MM-DD`, others as full timestamps, some omit required fields, some send extension data your parser doesn't recognize.

**What we learned:** validate at the boundary, log the failures, never crash the pipeline.

```java
@Component
public class FhirValidator {
    private final FhirValidator validator;
    
    public ValidationResult validate(IBaseResource resource) {
        ValidationResult result = validator.validateWithResult(resource);
        if (!result.isSuccessful()) {
            log.warn("fhir.validation.failed resource={} errors={}",
                resource.fhirType(), result.getMessages());
            // do NOT throw — route to dead-letter for human review
        }
        return result;
    }
}
```

Bad validation handling caused 4 of our 15 incidents. Fixed it once, gone forever.

---

## Lesson 2: Idempotency or death

Healthcare integrations retry. A lot. Network blips, gateway timeouts, scheduler restarts — every one triggers a retry. If your handler isn't idempotent, you create duplicate `Observation` records for one blood test. Patients now appear to have run a CBC twice.

**The fix:** every inbound FHIR message has a deterministic ID. Use it.

```java
public Observation upsert(Observation obs) {
    String idempotencyKey = obs.getIdentifierFirstRep().getValue();
    
    return observationRepo.findByIdempotencyKey(idempotencyKey)
        .orElseGet(() -> observationRepo.save(obs.withKey(idempotencyKey)));
}
```

We turned every write into an upsert keyed on a stable business key. Duplicate-record bugs dropped to zero.

---

## Lesson 3: The clock is not your friend

Different sources stamp their FHIR resources with different time zones. UTC, IST, sometimes naïve local time with no zone. Sometimes the clock is wrong.

**Rules I now follow:**
1. Parse everything to `Instant` at ingress — never `LocalDateTime`.
2. Store as UTC in the database.
3. Format to user's locale only at the edge (controller / response mapper).
4. If a timestamp has no zone, treat it as suspect and log it.

Caused 3 of our incidents. Twice the bug was "patient timeline shows future appointment" because someone stored IST as UTC.

---

## Lesson 4: Don't trust the network — design for partial failure

FHIR integrations are a graph of remote calls: ingress webhook → validation → transform → enrichment from EHR → push to insurer. Anywhere in the chain can fail.

**Patterns that work:**
- Every step is independently retryable
- Every step writes to a durable store (DB or queue) before moving on
- A failed step doesn't block other patients' messages
- A circuit breaker protects you from a slow downstream

We standardized on this pattern after an incident where one slow insurer API caused a thread pool to fill and blocked all unrelated patient traffic. Resilience4j circuit breaker fixed it permanently.

---

## Lesson 5: Logging structure matters more than log volume

When you're paged at 2am, you don't want to grep 10GB of unstructured logs. You want one query.

We moved every log line to structured JSON with these fields:
- `correlation_id` — uniquely identifies a patient message across all services
- `tenant_id` — which hospital/clinic
- `resource_type` — Patient, Observation, etc.
- `event` — what just happened
- `duration_ms` — how long it took
- `outcome` — success / failure / partial

One query against our log store told us which tenant, which resource, which step, what went wrong. MTTR (mean time to recovery) for incidents dropped from ~40 minutes to ~8.

---

## Lesson 6: PII logging will get you in trouble

You will not log patient names. You will not log SSNs / Aadhaar numbers. You will not log diagnoses. Period.

What you can log:
- Resource type, resource ID hash, tenant ID
- Timestamps, durations, outcomes
- Sanitized field-presence (e.g., "had_address=true", not the address)

We added a pre-commit hook that scanned every PR for "obvious PII leak" patterns. Caught 2 leaks before they shipped.

---

## Lesson 7: The on-call rotation is the best teacher

Six months into my role, my manager added me to on-call rotation. I was nervous. It was the single best decision for my engineering growth.

You learn things on-call you cannot learn anywhere else:
- What your system actually does at 3am
- Which logs are useful and which are noise
- Which alerts are signal and which are noise
- How a small bug in deployment becomes a customer-impacting incident in 12 minutes

If your role lets you opt into on-call, do it. It's the fastest engineering compounding you can get.

---

## The compounding effect

After 15 months at IHX, I wasn't just "the Spring Boot guy from Masai." I was someone who'd debugged production at 2am, understood SLOs, had a feel for trade-offs between consistency and availability. That changed everything about how I approached engineering interviews afterwards.

It's also why I now work on integration platforms at AlignBits — the patterns are the same. Different domain, same engineering rules.

---

## If you're starting in healthcare backend

1. **Read the HAPI FHIR docs**. The 80% you need fits in a weekend.
2. **Get familiar with one EHR's API** (Epic FHIR sandbox is free).
3. **Pick a real test fixture set**. Synthea generates realistic FHIR data.
4. **Get on a real on-call rotation as soon as you can**.
5. **Find a senior engineer who'll review your code line-by-line**. Mine made me 3x as good in 6 months.

---

*Shubham Bhati is a Backend Engineer at MobilePe Fintech. Based in Noida, India. [Portfolio](https://shubh2-0.github.io) · [GitHub](https://github.com/Shubh2-0) · [LinkedIn](https://linkedin.com/in/bhatishubham)*

---

**Publishing checklist:**
- [ ] Cover image: abstract flow diagram or HL7 FHIR logo
- [ ] Tags: `#java` `#springboot` `#healthcare` `#fhir` `#hapifhir` `#backend` `#productionengineering` `#microservices`
- [ ] Add a "FHIR resources" link section at the bottom for SEO
- [ ] Cross-post to Dev.to and Hashnode after 24h
