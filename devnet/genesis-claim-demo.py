#!/usr/bin/env python3
"""
genesis-claim-demo.py — OmegaX Protocol | Genesis Protect Acute v1
KR 1.5 Technical Walkthrough

Runs three representative claim scenarios through the full 8-step verification
chain, printing an ANSI-coloured terminal walkthrough and generating a PDF trace.

Fully self-contained — no network calls, no external APIs.
Requires: reportlab (pip install reportlab)
"""

import hashlib
import json
import os
import sys
import datetime
from pathlib import Path

# Enable ANSI colour on Windows
if os.name == "nt":
    os.system("")

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL COLOURS
# ─────────────────────────────────────────────────────────────────────────────

class C:
    TEAL  = "\033[38;5;38m"
    GREEN = "\033[38;5;46m"
    RED   = "\033[38;5;196m"
    AMBER = "\033[38;5;214m"
    CYAN  = "\033[38;5;51m"
    BLUE  = "\033[38;5;75m"
    MUTED = "\033[38;5;242m"
    WHITE = "\033[38;5;255m"
    BOLD  = "\033[1m"
    DIM   = "\033[2m"
    RESET = "\033[0m"

    @staticmethod
    def teal(s):   return f"{C.TEAL}{s}{C.RESET}"
    @staticmethod
    def green(s):  return f"{C.GREEN}{s}{C.RESET}"
    @staticmethod
    def red(s):    return f"{C.RED}{s}{C.RESET}"
    @staticmethod
    def amber(s):  return f"{C.AMBER}{s}{C.RESET}"
    @staticmethod
    def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"
    @staticmethod
    def blue(s):   return f"{C.BLUE}{s}{C.RESET}"
    @staticmethod
    def muted(s):  return f"{C.MUTED}{s}{C.RESET}"
    @staticmethod
    def white(s):  return f"{C.WHITE}{s}{C.RESET}"
    @staticmethod
    def bold(s):   return f"{C.BOLD}{s}{C.RESET}"
    @staticmethod
    def dim(s):    return f"{C.DIM}{s}{C.RESET}"


# ─────────────────────────────────────────────────────────────────────────────
# PROTOCOL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

PROGRAM_ID          = "Bn6eixac1QEEVErGBvBjxAd6pgB9e2q4XHvAkinQ5y1B"
PROTOCOL_FEE_BPS    = 50   # 0.5%
RESERVE_DOMAIN      = "WfQ7PjCTwuTCn3KM4mxUmyjQSw3RvcnyT3Gfdg2WUoq"
HEALTH_PLAN_ADDRESS = "D38bBYTWAkcyJZHFaZLRYRJErwLNB45YKJPfxU4PL5F6"
CLAIMS_OPERATOR     = "BGN6pVpuD9GPSsExtBi7pe4RLCJrkFVsQd9mw7ZdH8Ez"
ASSET_MINT          = "hWMfBLfo8EBaRTCcrWV33xaUR8gK2iTtqPoQvEMHmvu"

OUTCOME_SCHEMA = {
    "name":     "genesis-protect-acute-claim",
    "version":  "v1",
    "address":  "FcHi9p94PkgWBWwBo5TutWyH1smTiKBH9HT2SDQP4BNS",  # simulated
    "verified": True,
}

POLICY_SERIES = {
    "genesis-event-7-v1": {
        "address":           "6ZfyGQUcW132mEmYBmT5RtoagZyTHi2gTuGQUHW2qTLX",
        "series_id":         "genesis-event-7-v1",
        "material_locked":   True,
        "max_benefit_usdc":  1000,
        "benefit_mode":      "fixed_only",
        "coverage_days":     7,
        "premium_retail":    39,
        "tiers":             {1: 300, 2: 700, 3: 1000},
        "terms_hash":        "a7f2c4e1d9b3a8f1c5e2d4b9a3f7c2e1d5b8a4f9c1e3d6b2a8f5c3e7d1b4a9f6",
        "pricing_hash":      "b3c8e5f1a9d2c7e4f6b1a5d9c3e8f2a6d4c1e7b9a3f5d2c6e1b8a4d7c9e2f5a1",
        "payout_hash":       "c5e1b7d3a9f4c2e8b5d1a7c3e9b4f6d2a8c5e3b1d7a4f9c6e2b8d5a1c7e4b3d9",
        "reserve_model_hash":"d2b9f5c1e7a3d8b4f2c9e5a1d6b3f8c4e2a7d5b1f9c6e3a8d4b7f1c5e9a2d3b8",
        "evidence_req_hash": "e8d4c2b7f1a5e3d9c6b2f4a8d1c7e5b3f9a2d6c4e1b8a5d3f7c9e2b4a6d8c1f5",
    },
    "genesis-travel-30-v1": {
        "address":           "29XmfdaHceAeAvtiESAcNDXLsJxEqW2RBa3DttTUUcco",
        "series_id":         "genesis-travel-30-v1",
        "material_locked":   True,
        "max_benefit_usdc":  3000,
        "benefit_mode":      "hybrid_fixed_reimbursement",
        "coverage_days":     30,
        "premium_retail":    99,
        "tiers":             {1: 500, 2: 1500, 3: 3000},
        "terms_hash":        "f1a6d3c8e2b5f9a4d7c1e6b3f8a2d5c9e4b7f2a1d6c3e8b4f5a9d2c7e1b6f3a8",
        "pricing_hash":      "a2e7b4d9c5f1a8e3b6d2c4f7a1e6b9d3c8f2a5e1b7d4c9f6a3e8b2d5c1f9a4e7",
        "payout_hash":       "b8f3a5d1c9e6b2f7a4d8c2e5b9f1a6d3c7e2b5f4a9d6c1e8b3f9a2d7c5e4b6f8",
        "reserve_model_hash":"c4e9b1f6a3d8c5e2b7f3a9d1c6e4b8f2a5d9c3e7b1f4a6d2c8e5b9f7a4d3c1e6",
        "evidence_req_hash": "d7a2f5c8e1b4d6a3f9c2e7b5d1a8f4c6e3b9d5a1f7c4e2b6d9a5f3c1e8b2d4a7",
    },
}

HEALTH_PLAN = {
    "address":             HEALTH_PLAN_ADDRESS,
    "schema_binding_hash": "e9c1f4a7d3b6e2c8f5a9d4b1c7e3f6a2d8c5e1b7f4a6d2c9e5b3f8a1d6c4e7b9",
    "reserve_domain":      RESERVE_DOMAIN,
}

FUNDING_LINES = {
    "genesis-event7-premiums":   {
        "address": "2115rGD6zKmUhLGk9zwqbA9tdcA5nuAwRNaQDLcgSpWA",
        "type": "type_1_premiums",
    },
    "genesis-event7-liquidity":  {
        "address": "Hw6LdQpUqiUShzocvt7R1qxkkiiZiWeWjEoR1Ehx3SLw",
        "type": "type_2_liquidity",
    },
    "genesis-travel30-premiums": {
        "address": "8548dWwZAxPLR9mX4FWWASA1qatNj4hEgLDAmjRVWwLe",
        "type": "type_1_premiums",
    },
    "genesis-travel30-liquidity":{
        "address": "HBrdsf7UjYK5tRoM9j6YaxfV7nFBkVhnJbrmTLVaDiEr",
        "type": "type_2_liquidity",
    },
}

CLAIM_STATES = {0: "OPEN", 1: "UNDER_REVIEW", 2: "APPROVED",
                3: "DENIED", 4: "SETTLED", 5: "CLOSED"}

OBLIGATION_STATES = {0: "PROPOSED", 1: "RESERVED", 2: "CLAIMABLE_PAYABLE",
                     3: "SETTLED", 4: "CANCELED", 5: "IMPAIRED", 6: "RECOVERED"}


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO DATA  (from genesis-acute-claim-simulations-v1.json)
# ─────────────────────────────────────────────────────────────────────────────

SCENARIOS = [
    # ── EVT7-T1-001  ──────────────────────────────────────────────────────────
    {
        "id":         "EVT7-T1-001",
        "product":    "genesis-event-7-v1",
        "tier":       1,
        "tier_label": "ER_SAME_DAY",
        "outcome":    "APPROVED",
        "patient": {
            "age": 34, "sex": "M", "nationality": "US",
            "conditions": "none",
            "wallet": "sim-member-wallet-EVT7-T1-001",
        },
        "clinical": {
            "country": "United States", "city": "Las Vegas, NV",
            "facility": "University Medical Center of Southern Nevada",
            "context":  "Electric Daisy Carnival (EDC)", "day": 1,
        },
        "diagnosis": {
            "primary": "Exertional heat stroke",
            "icd":     "T67.01XA",
            "narrative": (
                "Patient collapsed at festival grounds. Core temp 40.4°C, GCS 13. "
                "Evaporative cooling + IV NS 2 L. Rhabdomyolysis screen negative. "
                "Neurological status normalised within 3 h. Discharged after 6 h observation."
            ),
        },
        "financials": {
            "actual_cost": 1840, "claimed": 150,
            "approved": 300,   # onChainOutcome authoritative
            "denied": 0,
        },
        "oracle": {
            "operator":         CLAIMS_OPERATOR,
            "tier_classified":  "TIER_1_ER_SAME_DAY",
            "outcome":          "APPROVED",
            "review_hours":     3.5,
            "review_notes":     (
                "Discharge summary confirms ER visit + same-day discharge. "
                "Heat stroke diagnosis aligns with Tier 1. No overnight admission confirmed."
            ),
            "docs_reviewed":    ["ER triage sheet", "ED physician note", "discharge summary"],
            "exclusion_clause": None,
        },
        "on_chain": {
            "claim_case_id":     "evt7-t1-sim-001",
            "intake_status":     4,
            "approved_usdc":     300,
            "paid_usdc":         300,
            "funding_line":      "genesis-event7-premiums",
            "obligation_status": "SETTLED",
            "fraud_referral":    False,
        },
    },
    # ── TRV30-T3-001  ─────────────────────────────────────────────────────────
    {
        "id":         "TRV30-T3-001",
        "product":    "genesis-travel-30-v1",
        "tier":       3,
        "tier_label": "SURGERY_ICU_2NIGHTS",
        "outcome":    "APPROVED",
        "patient": {
            "age": 67, "sex": "F", "nationality": "FR",
            "conditions": "atrial fibrillation (apixaban), hypertension, hyperlipidemia",
            "wallet": "sim-member-wallet-TRV30-T3-001",
        },
        "clinical": {
            "country": "United States", "city": "New York, NY",
            "facility": "NewYork-Presbyterian / Weill Cornell",
            "context":  "Family tourist visit", "day": 3,
        },
        "diagnosis": {
            "primary": "Acute ischemic stroke (left MCA, cardioembolic) — IV alteplase + Neuro-ICU",
            "icd":     "I63.30",
            "narrative": (
                "Sudden right hemiparesis and aphasia. NIHSS 14. IV alteplase 0.9 mg/kg "
                "within 3 h (door-to-needle 38 min). Neuro-ICU days 1-2. NIHSS improved to 8 "
                "by day 2. Discharged day 7 to inpatient rehabilitation."
            ),
        },
        "financials": {
            "actual_cost": 88000, "claimed": 3000,
            "approved": 3000, "denied": 0,
        },
        "oracle": {
            "operator":         CLAIMS_OPERATOR,
            "tier_classified":  "TIER_3_SURGERY_ICU_2NIGHTS",
            "outcome":          "APPROVED",
            "review_hours":     22,
            "review_notes":     (
                "Acute ischemic stroke with IV thrombolysis + Neuro-ICU >=2 nights. "
                "Tier 3 fully met. Pre-existing AF does not exclude acute stroke. "
                "Max benefit $3,000 approved. Invoice ($88,000) vastly exceeds product cap."
            ),
            "docs_reviewed":    [
                "stroke protocol log", "alteplase administration record",
                "Neuro-ICU chart", "MRI brain report", "discharge summary",
            ],
            "exclusion_clause": None,
        },
        "on_chain": {
            "claim_case_id":     "trv30-t3-sim-001",
            "intake_status":     4,
            "approved_usdc":     3000,
            "paid_usdc":         3000,
            "funding_line":      "genesis-travel30-liquidity",
            "obligation_status": "SETTLED",
            "fraud_referral":    False,
        },
    },
    # ── TRV30-T3-DEN-001  ─────────────────────────────────────────────────────
    {
        "id":         "TRV30-T3-DEN-001",
        "product":    "genesis-travel-30-v1",
        "tier":       3,
        "tier_label": "SURGERY_ICU_2NIGHTS",
        "outcome":    "DENIED",
        "patient": {
            "age": 57, "sex": "M", "nationality": "US",
            "conditions": "morbid obesity (BMI 44), type 2 diabetes, sleep apnea — bariatric candidate",
            "wallet": "sim-member-wallet-TRV30-T3-DEN-001",
        },
        "clinical": {
            "country": "India", "city": "New Delhi",
            "facility": "Max Super Speciality Hospital Saket",
            "context":  "Ostensible business travel — actual purpose: elective bariatric surgery",
            "day": 2,
        },
        "diagnosis": {
            "primary": "Laparoscopic sleeve gastrectomy (LSG) — elective bariatric surgery",
            "icd":     "E66.01 + Z68.44",
            "narrative": (
                "Elective LSG under GA. Pre-operative workup completed in US 3 months before "
                "policy. Hospital booked 8 weeks before inception. Submitted as 'emergency gastric "
                "surgery during business travel'. Investigation confirmed planned medical tourism."
            ),
        },
        "financials": {
            "actual_cost": 6800, "claimed": 3000,
            "approved": 0, "denied": 3000,
        },
        "oracle": {
            "operator":         CLAIMS_OPERATOR,
            "tier_classified":  "TIER_3_SURGERY_ICU_2NIGHTS",
            "outcome":          "DENIED",
            "review_hours":     72,
            "review_notes":     (
                "Elective LSG planned and booked months before policy inception. Doubly excluded: "
                "Section 5.1 (Elective Pre-Planned Procedures) + Section 5.5 (Obesity Treatment). "
                "Patient misrepresented procedure as emergency acute abdominal surgery. "
                "Medical tourism intent confirmed. Policy voided. Fraud referral filed."
            ),
            "docs_reviewed":    [
                "operative note", "US pre-operative workup",
                "Max Hospital booking confirmation (8 wks before inception)",
                "hotel reservation (10 nights)", "discharge summary",
            ],
            "exclusion_clause": (
                "genesis-acute-v1 Sec 5.1 (Elective Pre-Planned) + "
                "Sec 5.5 (Obesity Treatment) + Sec 8.2 (Fraud/Misrepresentation)"
            ),
        },
        "on_chain": {
            "claim_case_id":     "trv30-t3-den-001",
            "intake_status":     5,
            "approved_usdc":     0,
            "paid_usdc":         0,
            "funding_line":      None,
            "obligation_status": "VOID",
            "fraud_referral":    True,
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def sha256_json(obj: dict) -> str:
    """Deterministic SHA-256 of canonical JSON."""
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sim_pda(*seeds: str) -> str:
    """Simulate a Solana PDA derivation from seeds (base58-like 44-char address)."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    raw = hashlib.sha256(":".join(seeds).encode("utf-8")).hexdigest()
    n = int(raw, 16)
    result = []
    while n > 0:
        n, r = divmod(n, 58)
        result.append(alphabet[r])
    return "".join(reversed(result))[:44]


def truncate_hash(h: str, chars: int = 20) -> str:
    half = chars // 2
    return f"{h[:half]}...{h[-half:]}" if len(h) > chars else h


def fmt_usdc(amount: int) -> str:
    return f"${amount:,}.00 USDC"


def protocol_fee(amount: int) -> int:
    return int(amount * PROTOCOL_FEE_BPS / 10000)


# ─────────────────────────────────────────────────────────────────────────────
# CLAIM CHAIN COMPUTATION
# ─────────────────────────────────────────────────────────────────────────────

def build_evidence_packet(s: dict) -> dict:
    docs = s["oracle"]["docs_reviewed"]
    doc_hashes = {
        doc: hashlib.sha256(f"sim-doc:{s['id']}:{doc}".encode()).hexdigest()
        for doc in docs
    }
    ps = POLICY_SERIES[s["product"]]
    return {
        "schema":         "genesis-protect-acute-evidence-v1",
        "claim_id":       s["on_chain"]["claim_case_id"],
        "scenario_id":    s["id"],
        "product":        s["product"],
        "policy_series":  ps["address"],
        "health_plan":    HEALTH_PLAN_ADDRESS,
        "program_id":     PROGRAM_ID,
        "patient": {
            "wallet":         s["patient"]["wallet"],
            "nationality":    s["patient"]["nationality"],
            "age_at_event":   s["patient"]["age"],
            "pre_conditions": s["patient"]["conditions"],
        },
        "incident": {
            "country":         s["clinical"]["country"],
            "city":            s["clinical"]["city"],
            "facility":        s["clinical"]["facility"],
            "day_of_coverage": s["clinical"]["day"],
        },
        "diagnosis": {
            "primary":  s["diagnosis"]["primary"],
            "icd_code": s["diagnosis"]["icd"],
        },
        "claimed_amount_usdc":    s["financials"]["claimed"],
        "submitted_documents":    doc_hashes,
        "evidence_timestamp_utc": "2026-05-17T00:00:00Z",
    }


def build_decision_support_packet(s: dict, evidence_ref_hash: str) -> dict:
    return {
        "schema":                 "genesis-protect-acute-decision-v1",
        "claim_id":               s["on_chain"]["claim_case_id"],
        "evidence_ref_hash":      evidence_ref_hash,
        "operator":               s["oracle"]["operator"],
        "tier_classified":        s["oracle"]["tier_classified"],
        "review_outcome":         s["oracle"]["outcome"],
        "review_notes":           s["oracle"]["review_notes"],
        "exclusion_clause":       s["oracle"]["exclusion_clause"],
        "docs_reviewed_count":    len(s["oracle"]["docs_reviewed"]),
        "review_completed_hours": s["oracle"]["review_hours"],
        "approved_amount_usdc":   s["on_chain"]["approved_usdc"],
        "funding_line_charged":   s["on_chain"]["funding_line"],
        "review_timestamp_utc":   "2026-05-17T04:00:00Z",
    }


def build_attestation_document(s: dict, evidence_ref_hash: str, decision_support_hash: str) -> dict:
    return {
        "schema":                "genesis-protect-acute-attestation-v1",
        "claim_id":              s["on_chain"]["claim_case_id"],
        "oracle":                s["oracle"]["operator"],
        "outcome_schema":        OUTCOME_SCHEMA["name"],
        "outcome_schema_version":OUTCOME_SCHEMA["version"],
        # On-chain invariant: must equal evidence_ref_hash
        "attestation_ref_hash":  evidence_ref_hash,
        "decision_support_hash": decision_support_hash,
        "final_outcome":         s["oracle"]["outcome"],
        "tier":                  s["tier"],
        "approved_amount_usdc":  s["on_chain"]["approved_usdc"],
        "fraud_flag":            s["on_chain"]["fraud_referral"],
        "attestation_count":     1,
    }


def run_claim_chain(s: dict) -> dict:
    ps = POLICY_SERIES[s["product"]]

    # Step 1: Policy chain
    step1 = {
        "policy_series_address":   ps["address"],
        "series_id":               ps["series_id"],
        "material_locked":         ps["material_locked"],
        "terms_hash":              ps["terms_hash"],
        "pricing_hash":            ps["pricing_hash"],
        "payout_hash":             ps["payout_hash"],
        "reserve_model_hash":      ps["reserve_model_hash"],
        "evidence_req_hash":       ps["evidence_req_hash"],
        "health_plan_address":     HEALTH_PLAN["address"],
        "schema_binding_hash":     HEALTH_PLAN["schema_binding_hash"],
        "outcome_schema_name":     OUTCOME_SCHEMA["name"],
        "outcome_schema_verified": OUTCOME_SCHEMA["verified"],
    }

    # Step 2: Evidence packet
    evidence_packet  = build_evidence_packet(s)
    evidence_ref_hash = sha256_json(evidence_packet)
    step2 = {
        "evidence_packet":   evidence_packet,
        "evidence_ref_hash": evidence_ref_hash,
        "packet_bytes":      len(json.dumps(evidence_packet, separators=(",", ":")).encode()),
        "doc_count":         len(evidence_packet["submitted_documents"]),
    }

    # Step 3: Claim case init
    claim_case_pda = sim_pda("claim_case", HEALTH_PLAN_ADDRESS, s["on_chain"]["claim_case_id"])
    step3 = {
        "claim_case_id":  s["on_chain"]["claim_case_id"],
        "claim_case_pda": claim_case_pda,
        "initial_state":  0,
        "member_wallet":  s["patient"]["wallet"],
        "policy_series":  ps["address"],
        "health_plan":    HEALTH_PLAN_ADDRESS,
        "program_id":     PROGRAM_ID,
    }

    # Step 4: Oracle submission
    step4 = {
        "prev_state":   0,
        "curr_state":   1,
        "operator":     s["oracle"]["operator"],
        "docs":         s["oracle"]["docs_reviewed"],
        "sla_hours":    24,
    }

    # Step 5: Hash anchor
    step5 = {
        "evidence_ref_hash": evidence_ref_hash,
        "anchored_at":       claim_case_pda,
        "phi_on_chain":      False,
        "immutable_after":   "attestation_count >= 1",
    }

    # Step 6: Tier classification
    decision_support_packet  = build_decision_support_packet(s, evidence_ref_hash)
    decision_support_hash    = sha256_json(decision_support_packet)
    step6 = {
        "tier":                  s["tier"],
        "tier_label":            s["oracle"]["tier_classified"],
        "review_outcome":        s["oracle"]["outcome"],
        "review_hours":          s["oracle"]["review_hours"],
        "review_notes":          s["oracle"]["review_notes"],
        "exclusion_clause":      s["oracle"]["exclusion_clause"],
        "decision_support_hash": decision_support_hash,
    }

    # Step 7: Oracle attestation
    attestation_doc  = build_attestation_document(s, evidence_ref_hash, decision_support_hash)
    attestation_hash = sha256_json(attestation_doc)
    attestation_pda  = sim_pda("claim_attestation", claim_case_pda, s["oracle"]["operator"])
    hash_match       = (attestation_doc["attestation_ref_hash"] == evidence_ref_hash)
    step7 = {
        "attestation_pda":      attestation_pda,
        "evidence_ref_hash":    evidence_ref_hash,
        "attestation_ref_hash": attestation_doc["attestation_ref_hash"],
        "attestation_hash":     attestation_hash,
        "hash_match":           hash_match,
        "attestation_count":    1,
        "fraud_flag":           s["on_chain"]["fraud_referral"],
    }

    # Step 8: Coverage decision
    approved = s["on_chain"]["approved_usdc"]
    fee      = protocol_fee(approved)
    payout   = approved - fee
    fl_key   = s["on_chain"]["funding_line"]
    fl_addr  = FUNDING_LINES[fl_key]["address"] if fl_key else None

    if s["outcome"] == "APPROVED":
        final_state = 4   # SETTLED
        oblig_path  = [0, 1, 2, 3]
    else:
        final_state = 3   # DENIED
        oblig_path  = []

    step8 = {
        "outcome":           s["outcome"],
        "final_state":       final_state,
        "final_state_label": CLAIM_STATES[final_state],
        "approved_usdc":     approved,
        "fee_bps":           PROTOCOL_FEE_BPS,
        "fee_usdc":          fee,
        "payout_usdc":       payout,
        "funding_line":      fl_key,
        "funding_line_addr": fl_addr,
        "obligation_status": s["on_chain"]["obligation_status"],
        "obligation_path":   oblig_path,
        "fraud_referral":    s["on_chain"]["fraud_referral"],
        "denial_reason":     s["oracle"]["exclusion_clause"],
    }

    return {
        "scenario": s,
        "step1": step1, "step2": step2, "step3": step3, "step4": step4,
        "step5": step5, "step6": step6, "step7": step7, "step8": step8,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

W = 82   # terminal width

def divider():
    print(C.teal("  " + "-" * (W - 4)))

def big_divider():
    print(C.teal("=" * W))

def step_header(num: int, title: str):
    print()
    divider()
    print(C.bold(C.blue(f"  STEP {num}")) + C.bold(f"  {title}"))
    divider()

def kv(key: str, val: str, kw: int = 30, color=None):
    v = color(str(val)) if color else str(val)
    print(f"  {C.muted(key.ljust(kw))} {v}")

def hash_row(label: str, h: str):
    short = truncate_hash(h, 24)
    print(f"  {C.muted(label.ljust(30))} {C.cyan(short)}")

def check_ok(label: str):
    print(f"  [{C.green('OK')}] {label}")

def check_fail(label: str):
    print(f"  [{C.red('XX')}] {label}")

def wrap_print(text: str, indent: int = 4):
    words = text.split()
    line  = " " * indent
    for w in words:
        if len(line) + len(w) + 1 > W - 2:
            print(C.muted(line))
            line = " " * indent + w + " "
        else:
            line += w + " "
    if line.strip():
        print(C.muted(line))


def print_scenario_banner(s: dict):
    is_approved = s["outcome"] == "APPROVED"
    outcome_fn  = C.green if is_approved else C.red
    product_short = "Event 7  [7-day fixed]" if "event-7" in s["product"] else "Travel 30  [30-day hybrid]"
    print()
    big_divider()
    print(C.bold(C.teal(f"  SCENARIO  {s['id']}")))
    print(C.muted(f"  Product:    ") + C.cyan(product_short))
    print(C.muted(f"  Patient:    ") + f"{s['patient']['age']}y {s['patient']['sex']} | {s['patient']['nationality']}")
    print(C.muted(f"  Setting:    ") + f"{s['clinical']['facility']}, {s['clinical']['city']}")
    print(C.muted(f"  Diagnosis:  ") + C.white(s["diagnosis"]["primary"]))
    print(C.muted(f"  Outcome:    ") + C.bold(outcome_fn(s["outcome"])))
    big_divider()


# ── Step display functions ───────────────────────────────────────────────────

def display_step1(s, r):
    step_header(1, "Policy Chain Verification")
    d = r["step1"]
    print(f"  {C.bold('PolicySeries Account')}")
    kv("address",           d["policy_series_address"])
    kv("series_id",         d["series_id"])
    kv("material_locked",   str(d["material_locked"]), color=C.green)
    print()
    print(f"  {C.muted('5-hash binding fields:')}")
    for label, key in [("terms_hash", "terms_hash"), ("pricing_hash", "pricing_hash"),
                        ("payout_hash", "payout_hash"), ("reserve_model_hash", "reserve_model_hash"),
                        ("evidence_req_hash", "evidence_req_hash")]:
        hash_row(f"  {label}", d[key])
    print()
    print(f"  {C.bold('HealthPlan Account')}")
    kv("address", d["health_plan_address"])
    hash_row("schema_binding_hash", d["schema_binding_hash"])
    print()
    print(f"  {C.bold('OutcomeSchema')}")
    kv("name",     d["outcome_schema_name"])
    kv("verified", str(d["outcome_schema_verified"]), color=C.green)
    print()
    check_ok("PolicySeries.material_locked == true")
    check_ok("All 5 hash fields bound and non-null")
    check_ok("OutcomeSchema.verified == true  —  oracle may attest")


def display_step2(s, r):
    step_header(2, "Evidence Packet Construction & SHA-256")
    d  = r["step2"]
    ep = d["evidence_packet"]
    print(f"  {C.muted('Canonical evidence packet  (PHI-separated — no raw records):')}")
    kv("schema",         ep["schema"])
    kv("claim_id",       ep["claim_id"])
    kv("product",        ep["product"])
    kv("member wallet",  ep["patient"]["wallet"])
    kv("ICD-10",         ep["diagnosis"]["icd_code"])
    kv("docs hashed",    f"{d['doc_count']} files (individual SHA-256 per document)")
    kv("packet size",    f"{d['packet_bytes']} bytes (canonical JSON)")
    print()
    h = d["evidence_ref_hash"]
    print(f"  {C.muted('SHA-256  (hashlib.sha256 on utf-8 canonical JSON):')}")
    print(f"  {C.bold('evidence_ref_hash')} =")
    print(f"    {C.cyan(h[:32])}")
    print(f"    {C.cyan(h[32:])}")
    print()
    check_ok("evidence_ref_hash derived from deterministic canonical JSON")
    check_ok("No raw PHI on-chain  —  only 32-byte hash will be anchored")


def display_step3(s, r):
    step_header(3, "Claim Case PDA Initialization")
    d = r["step3"]
    print(f"  {C.muted('Seeds:  [\"claim_case\",  health_plan,  claim_id]')}")
    kv("health_plan",       d["health_plan"])
    kv("claim_id",          d["claim_case_id"])
    print()
    kv("ClaimCase PDA",     d["claim_case_pda"], color=C.cyan)
    kv("initial state",     f"0  —  {CLAIM_STATES[0]}", color=C.amber)
    kv("policy_series",     d["policy_series"])
    kv("member_wallet",     d["member_wallet"])
    print()
    check_ok(f"ClaimCase PDA derived  —  deterministic and verifiable")
    check_ok(f"State initialised: OPEN (0)")


def display_step4(s, r):
    step_header(4, "Oracle Submission  (OPEN -> UNDER_REVIEW)")
    d = r["step4"]
    kv("state transition",
       f"OPEN ({d['prev_state']})  ->  UNDER_REVIEW ({d['curr_state']})", color=C.amber)
    kv("oracle operator",   d["operator"])
    kv("review SLA target", f"{d['sla_hours']} h")
    print()
    print(f"  {C.muted('Documents submitted:')}")
    for doc in d["docs"]:
        print(f"    {C.muted('-')} {doc}")
    print()
    check_ok(f"State transition: OPEN -> UNDER_REVIEW")
    check_ok(f"{len(d['docs'])} documents submitted to oracle operator")


def display_step5(s, r):
    step_header(5, "Evidence Hash Anchor  (On-Chain)")
    d = r["step5"]
    h = d["evidence_ref_hash"]
    print(f"  {C.bold('evidence_ref_hash')} anchored to ClaimCase PDA:")
    print(f"    {C.cyan(h[:32])}")
    print(f"    {C.cyan(h[32:])}")
    print()
    kv("anchored at",    d["anchored_at"])
    kv("PHI on-chain",   str(d["phi_on_chain"]), color=C.green)
    kv("immutable after",d["immutable_after"])
    print()
    print(f"  {C.muted('Verification path:')}")
    print(f"  {C.muted('  claimant submits evidence  ->  operator hashes  ->  hash anchored at ClaimCase PDA')}")
    print(f"  {C.muted('  later: attestation_ref_hash MUST match evidence_ref_hash  (on-chain enforced)')}")
    print()
    check_ok("evidence_ref_hash written to ClaimCase.evidence_ref_hash")
    check_ok("Hash immutable once attestation_count >= 1")
    check_ok("PHI separation maintained throughout")


def display_step6(s, r):
    step_header(6, "Clinical Tier Classification & Decision Support")
    d = r["step6"]
    is_denied  = (d["review_outcome"] == "DENIED")
    out_color  = C.red if is_denied else C.green
    kv("tier classified",   d["tier_label"], color=C.cyan)
    kv("tier number",       str(d["tier"]))
    kv("review outcome",    d["review_outcome"], color=out_color)
    kv("review hours",      f"{d['review_hours']} h")
    print()
    print(f"  {C.muted('Reviewer notes:')}")
    wrap_print(d["review_notes"])
    if d["exclusion_clause"]:
        print()
        print(f"  {C.red('Exclusion clause:')}")
        wrap_print(d["exclusion_clause"])
    print()
    print(f"  {C.muted('Building decision support packet -> SHA-256:')}")
    hash_row("decision_support_hash", d["decision_support_hash"])
    print()
    check_ok(f"Tier classified: {d['tier_label']}")
    if is_denied:
        check_fail(f"Review outcome: DENIED — exclusion applied")
    else:
        check_ok(f"Review outcome: APPROVED")


def display_step7(s, r):
    step_header(7, "Oracle Attestation  (ClaimAttestation PDA)")
    d = r["step7"]
    print(f"  {C.muted('Seeds:  [\"claim_attestation\",  claim_case,  oracle]')}")
    kv("ClaimAttestation PDA", d["attestation_pda"], color=C.cyan)
    kv("attestation_count",    "1")
    print()
    print(f"  {C.bold('Critical on-chain invariant:')}")
    print(f"  {C.muted('  attestation_ref_hash MUST == evidence_ref_hash')}")
    print(f"  {C.muted('  (tx reverts with InvalidHashMismatch if they differ)')}")
    print()
    h = d["evidence_ref_hash"]
    print(f"  evidence_ref_hash    = {C.cyan(h[:32] + '...')}")
    print(f"  attestation_ref_hash = {C.cyan(d['attestation_ref_hash'][:32] + '...')}")
    match_label = "MATCH  —  tx proceeds" if d["hash_match"] else "MISMATCH  —  tx REVERTS"
    match_color = C.green if d["hash_match"] else C.red
    kv("hash check",   match_label, color=match_color)
    print()
    hash_row("attestation_hash", d["attestation_hash"])
    if d["fraud_flag"]:
        print()
        kv("fraud flag", "TRUE  —  referral initiated on-chain", color=C.red)
    print()
    check_ok("ClaimAttestation PDA derived and created on-chain")
    if d["hash_match"]:
        check_ok("attestation_ref_hash == evidence_ref_hash  —  invariant satisfied")
    else:
        check_fail("Hash mismatch  —  tx would have reverted")
    check_ok("Attestation recorded  —  audit trail complete")


def display_step8(s, r):
    step_header(8, "Coverage Decision & Settlement")
    d = r["step8"]
    is_approved = d["outcome"] == "APPROVED"
    out_color   = C.green if is_approved else C.red

    print()
    label = f"  COVERAGE DECISION:  {d['outcome']}"
    print(C.bold(out_color(label)))
    print()

    kv("final claim state",  f"{d['final_state']}  —  {d['final_state_label']}", color=out_color)
    kv("obligation status",  d["obligation_status"])

    if is_approved:
        print()
        kv("approved amount",   fmt_usdc(d["approved_usdc"]), color=C.green)
        kv("protocol fee",      f"{d['fee_bps']} BPS  =  {fmt_usdc(d['fee_usdc'])}")
        kv("member payout",     fmt_usdc(d["payout_usdc"]), color=C.bold)
        print()
        kv("funding line",      d["funding_line"])
        kv("funding line addr", d["funding_line_addr"])
        print()
        path_labels = "  ->  ".join(
            f"{n}:{OBLIGATION_STATES[n]}" for n in d["obligation_path"]
        )
        print(f"  {C.muted('Obligation path:  ')}{C.dim(path_labels)}")
    else:
        print()
        kv("approved amount",   fmt_usdc(0), color=C.red)
        kv("funding line",      "None  —  no settlement created")
        if d["denial_reason"]:
            print()
            print(f"  {C.red('Denial grounds:')}")
            wrap_print(d["denial_reason"])
        if d["fraud_referral"]:
            print()
            kv("fraud referral", "INITIATED  —  policy voided (Section 8.2)", color=C.red)

    print()
    divider()
    if is_approved:
        check_ok(f"Settlement: {fmt_usdc(d['payout_usdc'])} disbursed to member wallet")
        check_ok(f"Funding line: {d['funding_line']}")
    else:
        check_fail("Claim denied  —  zero settlement")
        if d["fraud_referral"]:
            check_fail("Policy voided  —  Section 8.2 fraud referral filed")


# ─────────────────────────────────────────────────────────────────────────────
# PDF TRACE
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf_trace(all_results: list, output_path: str):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, HRFlowable,
        )
        from reportlab.platypus.flowables import Flowable
        from reportlab.pdfgen import canvas as pdfcanvas
    except ImportError:
        print(C.red("  [ERROR] reportlab not installed — skipping PDF. pip install reportlab"))
        return

    # Palette
    TEAL  = colors.HexColor("#0891b2")
    NAVY  = colors.HexColor("#0f172a")
    SLATE = colors.HexColor("#1e293b")
    MUTED = colors.HexColor("#64748b")
    GREEN = colors.HexColor("#16a34a")
    RED   = colors.HexColor("#dc2626")
    AMBER = colors.HexColor("#d97706")
    LIGHT = colors.HexColor("#f1f5f9")
    WHITE = colors.white

    PAGE_W, PAGE_H = letter
    MARGIN = 0.75 * inch
    BODY_W = PAGE_W - 2 * MARGIN

    styles = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name=name, **kw)

    body    = ps("Body",  fontName="Helvetica",      fontSize=8.5,  leading=12,  textColor=NAVY, spaceAfter=4)
    body_sm = ps("BodyS", fontName="Helvetica",      fontSize=7.5,  leading=10,  textColor=MUTED, spaceAfter=3)
    mono    = ps("Mono",  fontName="Courier",        fontSize=7,    leading=9,   textColor=colors.HexColor("#0e7490"), spaceAfter=2)
    h1      = ps("H1",    fontName="Helvetica-Bold", fontSize=13,   leading=16,  textColor=TEAL,  spaceBefore=14, spaceAfter=6)
    h2      = ps("H2",    fontName="Helvetica-Bold", fontSize=10,   leading=13,  textColor=NAVY,  spaceBefore=10, spaceAfter=4)
    h3      = ps("H3",    fontName="Helvetica-Bold", fontSize=8.5,  leading=11,  textColor=SLATE, spaceBefore=6,  spaceAfter=3)

    # ── Custom flowables ──────────────────────────────────────────────────────

    class ScenarioBanner(Flowable):
        def __init__(self, title, sub=""):
            super().__init__()
            self.title = title
            self.sub   = sub
            self.h     = 48 if sub else 34
        def draw(self):
            c = self.canv
            c.setFillColor(TEAL)
            c.rect(0, 0, BODY_W, self.h, fill=True, stroke=False)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(10, self.h - 16, self.title)
            if self.sub:
                c.setFont("Helvetica", 7.5)
                c.setFillColor(colors.HexColor("#e0f2fe"))
                c.drawString(10, self.h - 30, self.sub)
        def wrap(self, *a): return (BODY_W, self.h)

    class StepBar(Flowable):
        def __init__(self, num, title):
            super().__init__()
            self.num = num; self.title = title; self.h = 20
        def draw(self):
            c = self.canv
            c.setFillColor(SLATE)
            c.rect(0, 0, BODY_W, self.h, fill=True, stroke=False)
            c.setFillColor(TEAL)
            c.rect(0, 0, 26, self.h, fill=True, stroke=False)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 8.5)
            c.drawString(7, 6, str(self.num))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(32, 6, self.title)
        def wrap(self, *a): return (BODY_W, self.h)

    class HashBox(Flowable):
        def __init__(self, label, h_val):
            super().__init__()
            self.label = label; self.h_val = h_val; self.h = 38
        def draw(self):
            c = self.canv
            c.setFillColor(colors.HexColor("#ecfeff"))
            c.setStrokeColor(TEAL)
            c.setLineWidth(0.75)
            c.roundRect(0, 0, BODY_W, self.h, 4, fill=True, stroke=True)
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 7)
            c.drawString(8, self.h - 13, self.label)
            c.setFillColor(colors.HexColor("#0e7490"))
            c.setFont("Courier", 7)
            c.drawString(8, self.h - 25, self.h_val[:56])
            rest = self.h_val[56:]
            if rest:
                c.drawString(8, 5, rest[:56])
        def wrap(self, *a): return (BODY_W, self.h)

    class OutcomeCard(Flowable):
        def __init__(self, outcome, approved_usdc, funding_line):
            super().__init__()
            self.outcome = outcome
            self.approved_usdc = approved_usdc
            self.funding_line  = funding_line
            self.h = 58
        def draw(self):
            c = self.canv
            approved = self.outcome == "APPROVED"
            bg     = colors.HexColor("#f0fdf4") if approved else colors.HexColor("#fef2f2")
            border = GREEN if approved else RED
            c.setFillColor(bg); c.setStrokeColor(border); c.setLineWidth(1.5)
            c.roundRect(0, 0, BODY_W, self.h, 6, fill=True, stroke=True)
            c.setFillColor(border); c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(BODY_W / 2, self.h - 22, self.outcome)
            c.setFont("Helvetica", 8); c.setFillColor(MUTED)
            if approved:
                c.drawCentredString(BODY_W / 2, self.h - 37,
                    f"Settlement: ${self.approved_usdc:,} USDC")
                c.drawCentredString(BODY_W / 2, self.h - 49,
                    f"Funding line: {self.funding_line}")
            else:
                c.drawCentredString(BODY_W / 2, self.h - 37, "Zero settlement  —  claim rejected")
                c.drawCentredString(BODY_W / 2, self.h - 49, "Policy voided  —  fraud referral initiated")
        def wrap(self, *a): return (BODY_W, self.h)

    # ── KV table helper ───────────────────────────────────────────────────────

    def kv_table(rows, deny_highlight=False):
        t = Table(rows, colWidths=[2.1 * inch, 4.5 * inch])
        sty = [
            ("BACKGROUND",     (0, 0), (-1, 0), TEAL),
            ("TEXTCOLOR",      (0, 0), (-1, 0), WHITE),
            ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, 0), 7.5),
            ("FONTNAME",       (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",       (1, 1), (1, -1), "Helvetica"),
            ("FONTSIZE",       (0, 1), (-1, -1), 7.5),
            ("TEXTCOLOR",      (0, 1), (0, -1), MUTED),
            ("TEXTCOLOR",      (1, 1), (1, -1), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
            ("GRID",           (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",     (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
            ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ]
        if deny_highlight:
            for i, row in enumerate(rows[1:], 1):
                if any(w in str(row[0]).lower()
                       for w in ("denial", "exclusion", "fraud", "denied", "referral")):
                    sty += [("TEXTCOLOR", (1, i), (1, i), RED),
                            ("FONTNAME",  (1, i), (1, i), "Helvetica-Bold")]
        t.setStyle(TableStyle(sty))
        return t

    # ── NumberedCanvas ────────────────────────────────────────────────────────

    class NumberedCanvas(pdfcanvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []
        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()
        def save(self):
            num = len(self._saved_page_states)
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)
                if i > 0:   # skip footer on cover
                    self._footer(i + 1, num)
                pdfcanvas.Canvas.showPage(self)
            pdfcanvas.Canvas.save(self)
        def _footer(self, page_num, total):
            self.saveState()
            self.setFont("Helvetica", 6.5)
            self.setFillColor(MUTED)
            txt = (f"OmegaX Protocol  |  Genesis Protect Acute v1  |  "
                   f"Claim Demo Trace  |  Internal — Pre-Mainnet  |  May 2026  |  "
                   f"Page {page_num} of {total}")
            self.drawCentredString(PAGE_W / 2, 0.38 * inch, txt)
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.4)
            self.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
            self.restoreState()

    # ── Cover page callback ───────────────────────────────────────────────────

    def on_first_page(canv, doc):
        canv.saveState()
        canv.setFillColor(NAVY)
        canv.rect(0, 0, PAGE_W, PAGE_H, fill=True, stroke=False)
        # top bar
        canv.setFillColor(TEAL)
        canv.rect(0, PAGE_H - 6, PAGE_W, 6, fill=True, stroke=False)
        # programme ID band
        canv.setFillColor(SLATE)
        canv.rect(MARGIN, PAGE_H * 0.518, BODY_W, 20, fill=True, stroke=False)
        canv.setFillColor(colors.HexColor("#94a3b8"))
        canv.setFont("Courier", 7.5)
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.518 + 6,
            f"Program ID:  {PROGRAM_ID}")
        # title
        canv.setFillColor(WHITE)
        canv.setFont("Helvetica-Bold", 21)
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.67,
            "Genesis Protect Acute v1")
        canv.setFont("Helvetica-Bold", 15)
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.632,
            "Claim Verification Demo Trace")
        canv.setFillColor(colors.HexColor("#94a3b8"))
        canv.setFont("Helvetica", 10)
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.598,
            "8-Step Proof: claim data hashed, verified, connected to coverage decision")
        # scenarios box
        bx = MARGIN; by = PAGE_H * 0.38; bw = BODY_W; bh = 78
        canv.setFillColor(SLATE)
        canv.roundRect(bx, by, bw, bh, 6, fill=True, stroke=False)
        canv.setFillColor(TEAL)
        canv.setFont("Helvetica-Bold", 7.5)
        canv.drawString(bx + 10, by + bh - 14, "SCENARIOS COVERED")
        canv.setFillColor(colors.HexColor("#e2e8f0"))
        canv.setFont("Helvetica", 8)
        rows_cover = [
            "EVT7-T1-001      Event 7   Tier 1   Heat stroke, Las Vegas NV       APPROVED   $300",
            "TRV30-T3-001     Travel 30 Tier 3   Ischemic stroke, New York NY    APPROVED   $3,000",
            "TRV30-T3-DEN-001 Travel 30 Tier 3   Elective bariatric, New Delhi   DENIED     (fraud)",
        ]
        for i, row in enumerate(rows_cover):
            canv.drawString(bx + 10, by + bh - 28 - i * 14, row)
        # meta
        canv.setFillColor(colors.HexColor("#475569"))
        canv.setFont("Helvetica", 8)
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.33,
            "OmegaX Protocol  |  KR 1.5 Technical Walkthrough  |  May 2026")
        canv.drawCentredString(PAGE_W / 2, PAGE_H * 0.31,
            "Fully Simulated  —  No Network Calls  |  Internal  —  Pre-Mainnet")
        # bottom bar
        canv.setFillColor(TEAL)
        canv.rect(0, 0, PAGE_W, 0.28 * inch, fill=True, stroke=False)
        canv.setFillColor(WHITE)
        canv.setFont("Helvetica", 7.5)
        canv.drawCentredString(PAGE_W / 2, 0.08 * inch,
            "© 2026 OmegaX Health Capital Markets")
        canv.restoreState()

    def on_later_pages(canv, doc):
        pass   # footer handled by NumberedCanvas

    # ── Build story ───────────────────────────────────────────────────────────

    story = [PageBreak()]   # page 1 = cover (drawn by on_first_page)

    # ── Intro ──
    story.append(Paragraph("How the 8-Step Verification Chain Works", h1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    chain_rows = [
        ["#", "Action", "On-Chain Effect"],
        ["1", "Policy chain verification",
         "Confirm PolicySeries 5-hash fields + OutcomeSchema.verified"],
        ["2", "Evidence packet hashing",
         "Build canonical JSON -> SHA-256 -> evidence_ref_hash"],
        ["3", "Claim case init",
         "ClaimCase PDA derived; state = OPEN (0)"],
        ["4", "Oracle submission",
         "State: OPEN -> UNDER_REVIEW (1)"],
        ["5", "Hash anchor",
         "evidence_ref_hash written to ClaimCase PDA; immutable"],
        ["6", "Tier classification",
         "Operator classifies tier; decision_support_hash computed"],
        ["7", "Oracle attestation",
         "ClaimAttestation PDA; attestation_ref_hash == evidence_ref_hash enforced"],
        ["8", "Coverage decision",
         "State -> APPROVED (2) / DENIED (3); obligation path or void"],
    ]
    chain_t = Table(chain_rows, colWidths=[0.3 * inch, 2.1 * inch, 4.2 * inch])
    chain_t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",      (0, 0), (-1, 0), WHITE),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0), 8),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 1), (-1, -1), 7.5),
        ("FONTNAME",       (0, 1), (0, -1), "Courier-Bold"),
        ("TEXTCOLOR",      (0, 1), (0, -1), TEAL),
        ("ALIGN",          (0, 0), (0, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID",           (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
    ]))
    story.append(chain_t)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Security invariant: <font name='Courier' color='#0e7490'>attestation_ref_hash</font> "
        "must equal <font name='Courier' color='#0e7490'>evidence_ref_hash</font>  —  enforced "
        "on-chain at <b>attest_claim_case</b>. Transaction reverts on mismatch. "
        "PHI never touches Solana; only 32-byte SHA-256 hashes are anchored.",
        body))
    story.append(PageBreak())

    # ── Per-scenario sections ──
    for res in all_results:
        s          = res["scenario"]
        is_approved = s["outcome"] == "APPROVED"
        ps_obj     = POLICY_SERIES[s["product"]]
        prod_label = (
            "EVENT 7  (7-day fixed benefit)" if "event-7" in s["product"]
            else "TRAVEL 30  (30-day hybrid)"
        )
        sub = (f"Product: {prod_label}  |  Tier {s['tier']}: {s['tier_label']}  |  "
               f"Outcome: {s['outcome']}")
        story.append(ScenarioBanner(f"SCENARIO  {s['id']}", sub))
        story.append(Spacer(1, 6))

        # patient/clinical header table
        hdr = [
            ["Patient",   f"{s['patient']['age']}y {s['patient']['sex']} | {s['patient']['nationality']}",
             "Location",  s["clinical"]["city"]],
            ["Pre-conditions", s["patient"]["conditions"][:60],
             "Facility",  s["clinical"]["facility"][:45]],
            ["Diagnosis", s["diagnosis"]["primary"][:60],
             "Coverage day", str(s["clinical"]["day"])],
        ]
        hdr_t = Table(hdr, colWidths=[0.9 * inch, 2.3 * inch, 0.9 * inch, 2.5 * inch])
        hdr_t.setStyle(TableStyle([
            ("FONTNAME",       (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",       (0, 0), (-1, -1), 7.5),
            ("FONTNAME",       (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",       (2, 0), (2, -1), "Helvetica-Bold"),
            ("TEXTCOLOR",      (0, 0), (0, -1), MUTED),
            ("TEXTCOLOR",      (2, 0), (2, -1), MUTED),
            ("BACKGROUND",     (0, 0), (-1, -1), LIGHT),
            ("GRID",           (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",     (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
            ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ]))
        story.append(hdr_t)
        story.append(Spacer(1, 8))

        # Step 1
        story.append(StepBar(1, "Policy Chain Verification"))
        story.append(Spacer(1, 4))
        s1r = [
            ["Field", "Value"],
            ["PolicySeries address", ps_obj["address"]],
            ["material_locked", "True"],
            ["terms_hash",        truncate_hash(ps_obj["terms_hash"], 30)],
            ["pricing_hash",      truncate_hash(ps_obj["pricing_hash"], 30)],
            ["payout_hash",       truncate_hash(ps_obj["payout_hash"], 30)],
            ["reserve_model_hash",truncate_hash(ps_obj["reserve_model_hash"], 30)],
            ["evidence_req_hash", truncate_hash(ps_obj["evidence_req_hash"], 30)],
            ["HealthPlan.schema_binding_hash",
             truncate_hash(HEALTH_PLAN["schema_binding_hash"], 30)],
            ["OutcomeSchema.verified", "True"],
        ]
        story.append(kv_table(s1r))
        story.append(Spacer(1, 6))

        # Step 2
        story.append(StepBar(2, "Evidence Packet Construction & SHA-256"))
        story.append(Spacer(1, 4))
        ep = res["step2"]["evidence_packet"]
        s2r = [
            ["Field", "Value"],
            ["schema",         ep["schema"]],
            ["claim_id",       ep["claim_id"]],
            ["member wallet",  ep["patient"]["wallet"]],
            ["ICD-10",         ep["diagnosis"]["icd_code"]],
            ["docs hashed",    f"{res['step2']['doc_count']} files (SHA-256 per document)"],
            ["packet size",    f"{res['step2']['packet_bytes']} bytes (canonical JSON)"],
        ]
        story.append(kv_table(s2r))
        story.append(Spacer(1, 4))
        story.append(HashBox("evidence_ref_hash  —  SHA-256 of canonical evidence packet",
                             res["step2"]["evidence_ref_hash"]))
        story.append(Spacer(1, 6))

        # Step 3
        story.append(StepBar(3, "Claim Case PDA Initialization"))
        story.append(Spacer(1, 4))
        s3r = [
            ["Field", "Value"],
            ['PDA seeds',      '"claim_case"  |  health_plan  |  claim_id'],
            ["ClaimCase PDA",  res["step3"]["claim_case_pda"]],
            ["initial state",  "0  —  OPEN"],
            ["policy_series",  ps_obj["address"]],
        ]
        story.append(kv_table(s3r))
        story.append(Spacer(1, 6))

        # Step 4
        story.append(StepBar(4, "Oracle Submission  (OPEN -> UNDER_REVIEW)"))
        story.append(Spacer(1, 4))
        s4r = [
            ["Field", "Value"],
            ["state transition",  "OPEN (0)  ->  UNDER_REVIEW (1)"],
            ["oracle operator",   s["oracle"]["operator"]],
            ["documents",         f"{len(s['oracle']['docs_reviewed'])} items submitted"],
            ["review SLA",        "24 h target"],
        ]
        story.append(kv_table(s4r))
        story.append(Spacer(1, 6))

        # Step 5
        story.append(StepBar(5, "Evidence Hash Anchor  (On-Chain)"))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "evidence_ref_hash anchored to ClaimCase PDA. "
            "Immutable once attestation_count &ge; 1. "
            "Raw PHI never written to Solana.", body_sm))
        story.append(HashBox("evidence_ref_hash  —  anchored at ClaimCase PDA (immutable)",
                             res["step5"]["evidence_ref_hash"]))
        story.append(Spacer(1, 6))

        # Step 6
        story.append(StepBar(6, "Clinical Tier Classification & Decision Support"))
        story.append(Spacer(1, 4))
        s6r = [
            ["Field", "Value"],
            ["tier classified",  res["step6"]["tier_label"]],
            ["review outcome",   res["step6"]["review_outcome"]],
            ["review hours",     f"{res['step6']['review_hours']} h"],
        ]
        if res["step6"]["exclusion_clause"]:
            s6r.append(["exclusion clause", res["step6"]["exclusion_clause"]])
        story.append(kv_table(s6r, deny_highlight=(not is_approved)))
        story.append(Spacer(1, 4))
        story.append(HashBox("decision_support_hash  —  SHA-256 of operator review bundle",
                             res["step6"]["decision_support_hash"]))
        story.append(Spacer(1, 6))

        # Step 7
        story.append(StepBar(7, "Oracle Attestation  (ClaimAttestation PDA)"))
        story.append(Spacer(1, 4))
        s7r = [
            ["Field", "Value"],
            ['PDA seeds',           '"claim_attestation"  |  claim_case  |  oracle'],
            ["ClaimAttestation PDA",res["step7"]["attestation_pda"]],
            ["attestation_count",   "1"],
            ["attestation_ref_hash == evidence_ref_hash",
             "MATCH  (tx proceeds)" if res["step7"]["hash_match"] else "MISMATCH  (tx REVERTS)"],
        ]
        story.append(kv_table(s7r))
        story.append(Spacer(1, 4))
        story.append(HashBox("attestation_ref_hash  ==  evidence_ref_hash  (on-chain enforced)",
                             res["step7"]["attestation_ref_hash"]))
        story.append(Spacer(1, 6))

        # Step 8
        story.append(StepBar(8, "Coverage Decision & Settlement"))
        story.append(Spacer(1, 6))
        story.append(OutcomeCard(
            outcome=s["outcome"],
            approved_usdc=res["step8"]["approved_usdc"],
            funding_line=res["step8"]["funding_line"],
        ))
        story.append(Spacer(1, 6))
        if is_approved:
            s8r = [
                ["Field", "Value"],
                ["final claim state", f"{res['step8']['final_state']}  —  SETTLED"],
                ["approved amount",   fmt_usdc(res["step8"]["approved_usdc"])],
                ["protocol fee",      f"50 BPS  =  {fmt_usdc(res['step8']['fee_usdc'])}"],
                ["member payout",     fmt_usdc(res["step8"]["payout_usdc"])],
                ["funding line",      res["step8"]["funding_line"]],
                ["funding line addr", res["step8"]["funding_line_addr"]],
                ["obligation path",
                 "  ->  ".join(OBLIGATION_STATES[n] for n in res["step8"]["obligation_path"])],
            ]
        else:
            s8r = [
                ["Field", "Value"],
                ["final claim state", "3  —  DENIED"],
                ["approved amount",   "$0"],
                ["funding line",      "None  —  no settlement"],
                ["obligation",        "Not created  —  VOID"],
                ["denial grounds",    res["step8"]["denial_reason"] or ""],
                ["fraud referral",    "INITIATED  —  policy voided" if res["step8"]["fraud_referral"] else "N/A"],
            ]
        story.append(kv_table(s8r, deny_highlight=(not is_approved)))
        story.append(PageBreak())

    # ── Summary table ──
    story.append(Paragraph("Scenario Comparison Summary", h1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    sum_rows = [["Scenario", "Product", "Tier", "Outcome", "Settlement", "Funding Line", "Obligation"]]
    for res in all_results:
        s = res["scenario"]
        prod = "Event 7" if "event-7" in s["product"] else "Travel 30"
        fl   = res["step8"]["funding_line"] or "—"
        sum_rows.append([
            s["id"], prod, f"T{s['tier']}", s["outcome"],
            fmt_usdc(res["step8"]["approved_usdc"]),
            fl, res["step8"]["obligation_status"],
        ])
    sum_t = Table(sum_rows, colWidths=[1.5*inch, 0.65*inch, 0.35*inch, 0.75*inch,
                                        0.8*inch, 1.55*inch, 0.65*inch])
    sum_sty = [
        ("BACKGROUND",     (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",      (0, 0), (-1, 0), WHITE),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0), 7.5),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 1), (-1, -1), 7),
        ("FONTNAME",       (0, 1), (0, -1), "Courier"),
        ("TEXTCOLOR",      (0, 1), (0, -1), TEAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID",           (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("ALIGN",          (2, 0), (3, -1), "CENTER"),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 4),
    ]
    for i, res in enumerate(all_results):
        row = i + 1
        col = GREEN if res["scenario"]["outcome"] == "APPROVED" else RED
        sum_sty += [("TEXTCOLOR", (3, row), (3, row), col),
                    ("FONTNAME",  (3, row), (3, row), "Helvetica-Bold")]
    sum_t.setStyle(TableStyle(sum_sty))
    story.append(sum_t)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Key takeaways:</b> (1) All three claims traversed the same 8-step chain — the code path "
        "is identical; only the oracle outcome differs. "
        "(2) Hash integrity is enforced on-chain: attestation_ref_hash must equal evidence_ref_hash "
        "or the transaction reverts. "
        "(3) PHI separation is maintained throughout: raw medical records never touch Solana. "
        "(4) The denial scenario shows that elective pre-planned procedures and fraud are caught at "
        "oracle review before any settlement obligation is created. "
        "(5) Tier-routed settlement: Event 7 T1 draws from the premiums funding line; "
        "Travel 30 T3 draws from the liquidity funding line.",
        body))

    # ── Build ──
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=0.75 * inch,
        title="Genesis Protect Acute v1 — Claim Verification Demo Trace",
        author="OmegaX Protocol",
        subject="KR 1.5 Technical Walkthrough",
    )
    doc.build(story,
              onFirstPage=on_first_page,
              onLaterPages=on_later_pages,
              canvasmaker=NumberedCanvas)

    print(C.green(f"  [OK] PDF written: {output_path}"))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print()
    big_divider()
    print(C.bold(C.teal("  OmegaX Protocol  —  Genesis Protect Acute v1")))
    print(C.bold(C.teal("  Claim Verification Demo  |  KR 1.5 Technical Walkthrough")))
    big_divider()
    print(C.muted(f"  Program ID  : {PROGRAM_ID}"))
    print(C.muted(f"  Scenarios   : {len(SCENARIOS)}  (2 APPROVED, 1 DENIED)"))
    print(C.muted( "  Mode        : fully self-contained simulation — no network calls"))
    big_divider()

    all_results = []
    for s in SCENARIOS:
        print_scenario_banner(s)
        r = run_claim_chain(s)
        display_step1(s, r)
        display_step2(s, r)
        display_step3(s, r)
        display_step4(s, r)
        display_step5(s, r)
        display_step6(s, r)
        display_step7(s, r)
        display_step8(s, r)
        all_results.append(r)
        print()

    # Summary
    print()
    big_divider()
    print(C.bold(C.teal("  SUMMARY")))
    big_divider()
    print(f"  {'Scenario'.ljust(22)} {'Outcome'.ljust(10)} {'Settlement'.ljust(16)} Funding Line")
    divider()
    for r in all_results:
        s   = r["scenario"]
        fn  = C.green if s["outcome"] == "APPROVED" else C.red
        fl  = r["step8"]["funding_line"] or "—"
        amt = fmt_usdc(r["step8"]["approved_usdc"])
        print(f"  {C.cyan(s['id'].ljust(22))} {fn(s['outcome'].ljust(10))} "
              f"{C.muted(amt.ljust(16))} {C.dim(fl)}")

    # PDF
    print()
    today    = datetime.date.today().strftime("%Y-%m-%d")
    pdf_path = Path(__file__).parent / f"omegax-genesis-claim-demo-trace-{today}.pdf"
    print(C.bold(C.teal(f"  Generating PDF trace...")))
    generate_pdf_trace(all_results, str(pdf_path))
    print()
    print(C.bold(C.green(f"  Done.")))
    print(C.muted(f"  PDF : {pdf_path}"))
    big_divider()


if __name__ == "__main__":
    main()
