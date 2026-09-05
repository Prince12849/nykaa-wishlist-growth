# Pilot provenance/source manifest

Pilot build date: 2 September 2026 (IST)

This pilot uses existing on-disk files only. No scraper was run and no raw file was modified.

| Source file | Role | Records used | Notes |
|---|---|---:|---|
| 'data/processed/survey/Fashion Shopping & Wishlist Preferences (Responses) - cleaned.xlsx' | Primary research | 20 respondents / 300 field units | All 20 respondents; 15 substantive fields per respondent. Timestamp and blank email field were not evidence units. |
| 'nykaa_reviews_tagged.csv' | Nykaa Play Store public reviews | 53 | Existing heuristic-tagged corpus; no stable review IDs or URLs. |
| 'nykaa_appstore_reviews_tagged.csv' | Nykaa App Store public reviews | 12 | Existing heuristic-tagged corpus; no stable review IDs or URLs. |
| 'research/all_reviews.csv' | Excluded | 0 | Derived combined snapshot intentionally excluded. |
| AJIO/Myntra files | Excluded from this pilot | 0 | AJIO blocked; Myntra frozen contextual evidence. |

## Sampling strata

The Nykaa review sample uses deterministic seeded selection for explicit wishlist/saved-item matches, pre-purchase hesitation, general friction, post-purchase complaints, and five controls from each HIGH/MEDIUM/LOW heuristic group.

## Classification provenance

The output schema follows the existing Discovery Engine prompt and taxonomy structure. The browser Anthropic engine was not executed because no API credential or secure backend is available. Labels are deterministic pre-labels for workflow testing only and remain human-review-pending; they are not AI classifications or validated findings.
