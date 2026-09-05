# Nykaa Fashion Wishlist-to-Purchase Case Study

## Project Objective

Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it, **without using discounts, coupons, deals, or other monetary incentives**.

This project follows a research-first product discovery process to identify the underlying user problem before committing to a solution.

---

## Current Project Status

- **Primary research:** 20 real survey responses covering wishlist usage, purchase outcomes, barriers, triggers, and desired product support.
- **Secondary research:** Public Nykaa Fashion app reviews, App Store reviews, YouTube comments, and Nykaa Fashion website/product evidence.
- **Discovery Engine:** Functional static browser prototype for organizing, classifying, reviewing, validating, and exploring research evidence.
- **Evidence validation:** Deterministic source-text validation layer supported by a human adjudication/audit layer.
- **MVP:** Functional wishlist decision-support prototype.
- **Case-study deck:** Presentation source and exports are maintained in `deck/`.
- **Final problem and solution:** Derived from the available evidence trail and documented in the case-study deliverables.

---

## Research-First Approach

The project separates evidence from interpretation and proposed decisions.

### Evidence labels

- **VERIFIED** — Directly supported by a reproducible artifact, source, dataset, or primary-research record.
- **HYPOTHESIS** — A testable proposition that has not yet been validated.
- **INFERENCE** — A reasoned interpretation of evidence rather than direct evidence.
- **PROPOSED** — A design, experiment, or future decision that has not yet been executed.

AI-generated classifications are treated as **candidate labels**, not as proof of user behaviour. Original source text and provenance are preserved wherever applicable.

---

## Evidence Pipeline

```text
Public + Primary Research
          ↓
Raw Source Material + Provenance
          ↓
Normalized Research Records
          ↓
AI-Assisted Candidate Classification
          ↓
Deterministic Evidence Validation
          ↓
Human Review / Exception Handling
          ↓
Quantified Patterns + Evidence Explorer
          ↓
Problem Definition + Hypotheses
          ↓
Non-Monetary Solution Options
          ↓
MVP + Success Metrics
          ↓
Case-Study Deck

## Repository Structure


nykaa-wishlist-growth/
│
├── analysis/
│   └── Analysis and evidence-validation outputs
│
├── data/
│   └── processed/
│       ├── pilot/
│       └── survey/
│
├── deck/
│   └── Case-study presentation assets
│
├── mvp/
│   ├── nykaa-discovery-engine/
│   │   ├── index.html
│   │   └── data/
│   │       └── nykaa_discovery_bundle.js
│   │
│   └── nykaa-wishlist-decision-support.html
│
├── research/
│   ├── qualitative/
│   │   └── interviews.pdf
│   ├── Research collection scripts
│   ├── Classification prompt
│   ├── Discovery Engine bundle builder
│   └── Research documentation
│
├── sources/
│   └── Supporting source registry
│
├── PROJECT_HANDOFF.md
├── PROJECT_STATUS.md
└── README.md