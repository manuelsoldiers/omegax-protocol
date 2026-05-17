# Genesis Protect Acute v1 — Claim Verification Demo Walkthrough

**KR 1.5 Deliverable** | OmegaX Protocol  
**Status:** Simulated devnet — no network calls  
**Audience:** Technical investors, auditors, protocol reviewers  
**Date:** May 2026

---

## Overview

This document walks through the KR 1.5 technical demonstration: three claim scenarios processed end-to-end through the OmegaX claim verification chain, showing how clinical evidence is hashed, committed on-chain, and connected to a binding coverage decision.

**What the demo proves:**

1. Claim evidence is reduced to a 32-byte SHA-256 hash before any interaction with Solana — raw PHI never touches the chain.
2. The oracle's attestation is cryptographically bound to the original evidence hash (`attestation_ref_hash == evidence_ref_hash` — enforced at the instruction level; the transaction reverts on mismatch).
3. Every material policy parameter is anchored in five immutable hash fields on the `PolicySeries` account before coverage can be issued.
4. The same 8-step code path handles both approvals and denials — fraud is caught at oracle review, before any settlement obligation is created.

**Artefacts:**

| File | Description |
|---|---|
| `devnet/genesis-claim-demo.py` | Self-contained Python script — runs terminal walkthrough + generates PDF |
| `devnet/omegax-genesis-claim-demo-trace-2026-05-17.pdf` | Rendered PDF trace (26 KB) |

**To reproduce:**

```bash
cd devnet
python genesis-claim-demo.py
```

Requires only `reportlab` (`pip install reportlab`). No network access, no wallet, no devnet connection.

---

## Protocol References

| Field | Value |
|---|---|
| Program ID | `Bn6eixac1QEEVErGBvBjxAd6pgB9e2q4XHvAkinQ5y1B` |
| HealthPlan account | `D38bBYTWAkcyJZHFaZLRYRJErwLNB45YKJPfxU4PL5F6` |
| Claims operator | `BGN6pVpuD9GPSsExtBi7pe4RLCJrkFVsQd9mw7ZdH8Ez` |
| OutcomeSchema | `genesis-protect-acute-claim v1` — `verified = true` |

---

## The 8-Step Verification Chain

Each scenario runs identically through the following chain. The code path does not branch until Step 6 (oracle review outcome).

| Step | Action | On-Chain Effect |
|---|---|---|
| 1 | **Policy chain verification** | Confirm `PolicySeries` 5-hash fields + `material_locked = true` + `OutcomeSchema.verified = true` |
| 2 | **Evidence packet hashing** | Canonical JSON built from claim metadata + doc hashes → `SHA-256` → `evidence_ref_hash` |
| 3 | **Claim case init** | `ClaimCase` PDA derived (`"claim_case" \| health_plan \| claim_id`); state = `OPEN (0)` |
| 4 | **Oracle submission** | State: `OPEN (0)` → `UNDER_REVIEW (1)` |
| 5 | **Hash anchor** | `evidence_ref_hash` written to `ClaimCase` PDA — immutable once `attestation_count ≥ 1` |
| 6 | **Tier classification** | Oracle classifies clinical tier; `decision_support_hash` computed from review bundle |
| 7 | **Oracle attestation** | `ClaimAttestation` PDA created; `attestation_ref_hash == evidence_ref_hash` enforced on-chain |
| 8 | **Coverage decision** | State → `APPROVED (2)` / `DENIED (3)`; obligation settled via funding line or voided |

> **Security invariant (Step 7):** `attest_claim_case` checks that `attestation_ref_hash == ClaimCase.evidence_ref_hash`. If the oracle attempts to attest a different evidence set — or if the evidence packet was tampered after anchoring — the transaction reverts with `InvalidHashMismatch`. This makes post-hoc evidence substitution impossible.

---

## Scenario 1 — EVT7-T1-001: Heat Stroke, Las Vegas NV

**Product:** Genesis Event 7 (7-day fixed benefit, max $1,000)  
**Patient:** 34y M | US national | No pre-existing conditions  
**Setting:** University Medical Center of Southern Nevada — Electric Daisy Carnival (EDC)  
**Diagnosis:** Exertional heat stroke (ICD-10: T67.01XA) — same-day ER discharge  
**Expected outcome:** APPROVED, Tier 1

### Step 2 — Evidence Packet Hashing

The evidence packet is assembled from claim metadata, patient profile, incident details, and individual SHA-256 hashes of three submitted documents. The packet is never sent to Solana:

```
schema          genesis-protect-acute-evidence-v1
claim_id        evt7-t1-sim-001
product         genesis-event-7-v1
member wallet   sim-member-wallet-EVT7-T1-001
ICD-10          T67.01XA
docs hashed     3 files (individual SHA-256 per document)
packet size     1,000 bytes (canonical JSON)

evidence_ref_hash =
  b19efc90ff8c147d1ac61bf94b550ffb
  09d26f3b1e7f7b312d824516da8d6ca4
```

### Step 3 — ClaimCase PDA

```
seeds         "claim_case" | D38bBYTWAkcyJZHFaZLRYRJErwLNB45YKJPfxU4PL5F6 | evt7-t1-sim-001
ClaimCase PDA  3giTWacLpUrruRFtMyB7jk3582aeM6TPVrSQKiFFprBd
initial state  0 — OPEN
```

### Step 6 — Oracle Review

Operator `BGN6pVpuD9GPSsExtBi7pe4RLCJrkFVsQd9mw7ZdH8Ez` reviews ER triage sheet, ED physician note, and discharge summary.

```
tier classified     TIER_1_ER_SAME_DAY
review outcome      APPROVED
review SLA          3.5 h
notes               "Discharge summary confirms ER visit + same-day discharge.
                     Heat stroke diagnosis aligns with Tier 1. No overnight admission confirmed."
```

### Step 7 — Oracle Attestation

```
ClaimAttestation PDA  Atcj4U8v8PygSQki7YzG8mWSP9Yo25xwLgWhwCsdfcav
attestation_count     1
attestation_ref_hash  b19efc90ff8c147d1ac61bf94b550ffb09d26f3b1e7f7b312d824516da8d6ca4
evidence_ref_hash     b19efc90ff8c147d1ac61bf94b550ffb09d26f3b1e7f7b312d824516da8d6ca4
hash check            MATCH — tx proceeds
```

### Step 8 — Coverage Decision

```
COVERAGE DECISION:  APPROVED

final claim state   4 — SETTLED
approved amount     $300.00 USDC
protocol fee        50 BPS = $1.00 USDC
member payout       $299.00 USDC
funding line        genesis-event7-premiums
funding line addr   2115rGD6zKmUhLGk9zwqbA9tdcA5nuAwRNaQDLcgSpWA
obligation path     PROPOSED -> RESERVED -> CLAIMABLE_PAYABLE -> SETTLED
```

> **Note on amounts:** Actual hospital bill was $1,840. Genesis Event 7 is a fixed-benefit product — Tier 1 pays a flat $300 regardless of the actual cost. The claimant is responsible for residual costs. The protocol fee of $1 (50 BPS) is deducted at settlement; net payout to the member is $299.

---

## Scenario 2 — TRV30-T3-001: Ischemic Stroke, New York NY

**Product:** Genesis Travel 30 (30-day hybrid UCR, max $3,000)  
**Patient:** 67y F | French national | AF (apixaban), hypertension, hyperlipidemia  
**Setting:** NewYork-Presbyterian / Weill Cornell Comprehensive Stroke Center  
**Diagnosis:** Acute ischemic stroke, left MCA territory — IV alteplase + Neuro-ICU ≥2 nights (ICD-10: I63.30)  
**Expected outcome:** APPROVED, Tier 3 — maximum benefit

### Step 2 — Evidence Packet Hashing

```
schema          genesis-protect-acute-evidence-v1
claim_id        trv30-t3-sim-001
product         genesis-travel-30-v1
member wallet   sim-member-wallet-TRV30-T3-001
ICD-10          I63.30
docs hashed     5 files (individual SHA-256 per document)
packet size     1,297 bytes (canonical JSON)

evidence_ref_hash =
  2b7ad70522338fd363215e80f858ac16
  39fbf045a15b5610739dfedfc9b984b0
```

### Step 3 — ClaimCase PDA

```
seeds         "claim_case" | D38bBYTWAkcyJZHFaZLRYRJErwLNB45YKJPfxU4PL5F6 | trv30-t3-sim-001
ClaimCase PDA  6wwFAD4xmxWutRaFW5zn25oaTZbBdefXJ8gqn1HtkfK6
initial state  0 — OPEN
```

### Step 6 — Oracle Review

Operator reviews stroke protocol log, alteplase administration record, Neuro-ICU chart, MRI brain report, and discharge summary.

```
tier classified     TIER_3_SURGERY_ICU_2NIGHTS
review outcome      APPROVED
review SLA          22.0 h
notes               "Acute ischemic stroke with IV thrombolysis + Neuro-ICU ≥2 nights.
                     Tier 3 fully met. Pre-existing AF does not exclude acute stroke.
                     Max benefit $3,000 approved. Invoice ($88,000) vastly exceeds product cap."
```

> **Pre-existing condition handling:** The patient has atrial fibrillation, which is a known risk factor for cardioembolic stroke. However, the acute stroke is a new, independent, covered event under genesis-acute-v1. The policy does not exclude outcomes arising *from* pre-existing conditions, only procedures *for* them.

### Step 7 — Oracle Attestation

```
ClaimAttestation PDA  Gy9w924dkdeDdkESE8VV2P3M24mKgPtX7Xyks9GA2uvC
attestation_count     1
attestation_ref_hash  2b7ad70522338fd363215e80f858ac1639fbf045a15b5610739dfedfc9b984b0
evidence_ref_hash     2b7ad70522338fd363215e80f858ac1639fbf045a15b5610739dfedfc9b984b0
hash check            MATCH — tx proceeds
```

### Step 8 — Coverage Decision

```
COVERAGE DECISION:  APPROVED

final claim state   4 — SETTLED
approved amount     $3,000.00 USDC
protocol fee        50 BPS = $15.00 USDC
member payout       $2,985.00 USDC
funding line        genesis-travel30-liquidity
funding line addr   HBrdsf7UjYK5tRoM9j6YaxfV7nFBkVhnJbrmTLVaDiEr
obligation path     PROPOSED -> RESERVED -> CLAIMABLE_PAYABLE -> SETTLED
```

> **Capital routing:** Travel 30 Tier 3 charges the **liquidity** funding line (not the premiums line), reflecting the capital structure: T1 claims are covered by premium flow; T2/T3 claims draw from LP-provided liquidity reserves. The $88,000 US hospital invoice vastly exceeds the $3,000 product cap — the policyholder bears residual costs.

---

## Scenario 3 — TRV30-T3-DEN-001: Elective Bariatric Surgery, New Delhi

**Product:** Genesis Travel 30 (30-day hybrid UCR, max $3,000)  
**Patient:** 57y M | US national | Morbid obesity (BMI 44), type 2 diabetes, sleep apnea — documented bariatric surgical candidate  
**Setting:** Max Super Speciality Hospital Saket, New Delhi — Bariatric Surgery Unit  
**Diagnosis:** Laparoscopic sleeve gastrectomy (LSG) — elective procedure (ICD-10: E66.01 + Z68.44)  
**Expected outcome:** DENIED — three independent grounds

### Step 2 — Evidence Packet Hashing

The chain runs identically up to Step 6. Evidence is still hashed and anchored:

```
schema          genesis-protect-acute-evidence-v1
claim_id        trv30-t3-den-001
product         genesis-travel-30-v1
member wallet   sim-member-wallet-TRV30-T3-DEN-001
ICD-10          E66.01 + Z68.44
docs hashed     5 files (individual SHA-256 per document)
packet size     1,357 bytes (canonical JSON)

evidence_ref_hash =
  7992a47adbebfdc3fc2a7bc8109df4c6
  723ccbbaaa49e08514f75efc3e26200e
```

### Step 3 — ClaimCase PDA

```
seeds         "claim_case" | D38bBYTWAkcyJZHFaZLRYRJErwLNB45YKJPfxU4PL5F6 | trv30-t3-den-001
ClaimCase PDA  7copPaMX8HTNMM7qrNQihE28bMKKLujpsyeJGPwH1Ydb
initial state  0 — OPEN
```

### Step 6 — Oracle Review

The investigator finds that the submitted claim is irreconcilable with the submitted documentation:

| Finding | Evidence |
|---|---|
| Pre-operative workup | Completed in the US **3 months before** policy inception |
| Hospital booking | Max Hospital confirmed **8 weeks before** inception |
| Accommodation | 10-night hotel reservation — inconsistent with "2-day business conference" |
| Conference documentation | Unverifiable — not confirmed |

```
tier classified     TIER_3_SURGERY_ICU_2NIGHTS
review outcome      DENIED
review SLA          72.0 h  (extended — fraud investigation)
exclusion clause    genesis-acute-v1 Sec 5.1 (Elective Pre-Planned Procedures)
                    + Sec 5.5 (Obesity Treatment and Weight-Loss Surgery)
                    + Sec 8.2 (Fraud and Misrepresentation)
```

The denial rests on **three independent grounds**, any one of which is sufficient:

1. **Section 5.1 — Elective/pre-planned:** Pre-operative workup dated 3 months before policy; hospital booking 8 weeks before inception. Acute medical necessity is absent.
2. **Section 5.5 — Excluded condition:** Bariatric and weight-loss surgery is explicitly excluded regardless of clinical indication.
3. **Section 8.2 — Misrepresentation:** The claimant described a planned elective procedure as "emergency gastric surgery during business travel". Policy voided retroactively; fraud referral filed.

### Step 7 — Oracle Attestation

The attestation still executes — the oracle attests to a denial outcome, and the hash invariant still holds:

```
ClaimAttestation PDA  Hb4tfkLjS7DSfn7LUeP8vRgC6Ji1kG9XGbopn2vtsBBF
attestation_count     1
attestation_ref_hash  7992a47adbebfdc3fc2a7bc8109df4c6723ccbbaaa49e08514f75efc3e26200e
evidence_ref_hash     7992a47adbebfdc3fc2a7bc8109df4c6723ccbbaaa49e08514f75efc3e26200e
hash check            MATCH — tx proceeds
fraud_flag            TRUE
```

### Step 8 — Coverage Decision

```
COVERAGE DECISION:  DENIED

final claim state   3 — DENIED
approved amount     $0
funding line        None — no settlement created
obligation          Not created — VOID
denial grounds      genesis-acute-v1 Sec 5.1 + Sec 5.5 + Sec 8.2
fraud referral      INITIATED — policy voided
```

> **Capital protection:** Because the denial happens at oracle review before any obligation is proposed, no funds are ever reserved or moved. The LP capital pool is not exposed to the fraudulent claim at any point in the settlement lifecycle.

---

## Scenario Comparison

| Scenario | Product | Tier | Outcome | Settlement | Funding Line | Obligation |
|---|---|---|---|---|---|---|
| EVT7-T1-001 | Event 7 | T1 | **APPROVED** | $299 USDC | `genesis-event7-premiums` | SETTLED |
| TRV30-T3-001 | Travel 30 | T3 | **APPROVED** | $2,985 USDC | `genesis-travel30-liquidity` | SETTLED |
| TRV30-T3-DEN-001 | Travel 30 | T3 | **DENIED** | $0 | — | VOID |

---

## Security Properties Demonstrated

### 1. Deterministic hash chain

`evidence_ref_hash` is computed as `SHA-256(canonical_json(evidence_packet))` where `canonical_json` uses `sort_keys=True`, `ensure_ascii=True`, and compact separators. The same input always produces the same hash — the chain is fully reproducible and independently verifiable by any party holding the original evidence packet.

### 2. PHI separation

The evidence packet contains metadata and per-document hashes, not raw clinical records. The 64-hex-char `evidence_ref_hash` written to the `ClaimCase` PDA is the only patient-linked datum on Solana. Medical records remain off-chain, accessible only to authorised parties.

### 3. Tamper-evident anchoring

Once `evidence_ref_hash` is written to `ClaimCase.evidence_ref_hash` and `attestation_count ≥ 1`, the field is immutable. Any attempt to re-attest with a different evidence set will fail the `attestation_ref_hash == evidence_ref_hash` check at the instruction level.

### 4. Uniform code path

All three scenarios — two approvals and one denial — traverse the identical 8-step chain. Fraud is not a special case; it is a normal oracle outcome (`review_outcome = "DENIED"`) that routes the obligation lifecycle to `VOID` instead of `SETTLED`. This means the denial path is as auditable as the approval path.

### 5. Capital isolation

Tier-based funding-line routing means that:
- Event 7 T1 claims draw from premium flow (`type_1_premiums`) — losses funded by collected premiums.
- Travel 30 T3 claims draw from LP liquidity reserves (`type_2_liquidity`) — as expected for high-severity events.
- Denied claims never touch any funding line.

---

## How to Run

```bash
# From repo root
python devnet/genesis-claim-demo.py
```

The script:
1. Runs all three scenarios end-to-end, printing ANSI-coloured step-by-step output to the terminal.
2. Generates a PDF trace at `devnet/omegax-genesis-claim-demo-trace-YYYY-MM-DD.pdf`.

No network access, no wallet keypair, no devnet connection required. All PDAs are simulated via deterministic SHA-256 derivation; all hashes are real `hashlib.sha256` outputs computed from the scenario data.

---

*OmegaX Protocol — KR 1.5 Technical Walkthrough — Internal, Pre-Mainnet — May 2026*
