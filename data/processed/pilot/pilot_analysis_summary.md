# AI Discovery Engine pilot analysis

Status: PILOT ONLY — no final problem statement or MVP decision.

## Execution caveat

The browser Discovery Engine was not executed because ANTHROPIC_API_KEY is absent and the HTML has no secure credential/backend boundary. Browser-engine AI coverage: 0%. Deterministic pre-label coverage: 365/365 (100.0%). All records remain human-review-pending.

## Pilot size

- Total pilot records: **365**
- Survey field-aware units: **300**
- Nykaa Play Store review units: **53**
- Nykaa App Store review units: **12**
- Full survey respondent count represented: **20**

## Records by source

| Source | Records |
|---|---:|
| survey | 300 |
| Play Store | 53 |
| App Store | 12 |

## Records by evidence type

| Evidence type | Records |
|---|---:|
| irrelevant_or_unclear | 140 |
| direct_wishlist_behavior | 97 |
| pre_purchase_hesitation | 86 |
| post_purchase_complaint | 39 |
| general_shopping_friction | 3 |

## Records by journey stage

| Journey stage | Records |
|---|---:|
| context | 139 |
| pre_purchase | 86 |
| wishlist_behavior | 60 |
| post_purchase | 39 |
| post_wishlist_outcome | 20 |
| wishlist_behavior_or_revisit | 17 |
| general_shopping | 3 |
| unknown | 1 |

## Records by wishlist linkage

| Wishlist linkage | Records |
|---|---:|
| not_mentioned | 177 |
| explicit_direct | 102 |
| explicit_pre_purchase | 80 |
| inferred_or_ambiguous | 6 |

## Theme distribution by source

### Survey

| Theme label | Field units |
|---|---:|
| other/unclear | 208 |
| value/price assessment | 53 |
| occasion/styling | 12 |
| quality/material confidence | 9 |
| fit/size confidence | 6 |
| deprioritization/memory | 5 |
| comparison/alternative | 3 |
| wishlist/UX discoverability | 3 |
| availability/stock | 1 |

### Play Store

| Theme label | Records |
|---|---:|
| wishlist/UX discoverability | 17 |
| other/unclear | 14 |
| value/price assessment | 7 |
| quality/material confidence | 4 |
| availability/stock | 3 |
| fit/size confidence | 3 |
| trust/authenticity | 3 |
| review/product-information confidence | 1 |
| comparison/alternative | 1 |

### App Store

| Theme label | Records |
|---|---:|
| availability/stock | 3 |
| other/unclear | 3 |
| review/product-information confidence | 2 |
| trust/authenticity | 2 |
| quality/material confidence | 1 |
| value/price assessment | 1 |

These are deterministic pre-label counts, not AI-validated user findings. Survey counts reflect field units, not unique respondents; public-review counts reflect a stratified sample, not platform prevalence.

## Heuristic relevance versus pilot classification

| Heuristic relevance -> evidence type | Records |
|---|---:|
| LOW -> post_purchase_complaint | 21 |
| HIGH -> direct_wishlist_behavior | 17 |
| HIGH -> post_purchase_complaint | 11 |
| MEDIUM -> post_purchase_complaint | 7 |
| LOW -> pre_purchase_hesitation | 5 |
| LOW -> general_shopping_friction | 2 |
| HIGH -> pre_purchase_hesitation | 1 |
| MEDIUM -> general_shopping_friction | 1 |

The existing HIGH/MEDIUM/LOW field is a keyword prefilter, not a causal or wishlist-specific label.

## False-positive candidates

- play_store_f136d042eb56940f — While proceeding to payment for first order I couldn't avail the '10% off on first order' The products went out of stock while placing the order, though the stock was seen available in the wishlist later on.
- play_store_a609a7ba9d01ff00 — Very faulty app. Unlike the nykaa beauty app this app is not user friendly. There is a problem in saving items to your wishlist it just does not get saved! In fact on their website their is no option to wishlist The FAQ 
- play_store_ad201146d6bc3212 — Customer support was excellent. I was in search for an item but couldn't find it. I went to the chat box and Stephanie from customer support helped me out instantly and saved my time.
- play_store_a97f7fa4d9edf0c1 — prices and cloth ranges are good but if i wishlist something for later it ends up either getting stocked out and never returns back in stock for months
- play_store_317de7fc102e81fc — First I add many items in cart,when I want to buy one thing from cart,,I have no option to buy just one thing from cart,,so I move to wishlist all items,after I order that selected item and continue shopping,,,please do 
- play_store_1548a35ad245ff5a — Great collection, but zero customer support. I've been waiting for my refund from nykaa fashion from past 11 days now but no response from their side 😒. And all this in the times where I get instant refunds from websites
- app_store_13ff23104d857eff — I received my order on time, but when I wanted to return it, the process took far too long and required multiple attempts. The delivery partner did not even call me, yet they falsely updated the status saying I was unava
- app_store_2a90097a9524966b — this is totally a fake application...and i believe all the positive reviews are paid. O am struggling a lot with my first time order. they have sent me the incomplete product where only shirt have been received and botto

## Ambiguous/unclear examples

- survey_r001_age_range — irrelevant_or_unclear; not_mentioned; 26–30
- survey_r001_current_city — irrelevant_or_unclear; not_mentioned; Bangalore
- survey_r001_online_fashion_shopping_frequency — irrelevant_or_unclear; not_mentioned; Every 2–3 months
- survey_r001_preferred_platform_clothing — irrelevant_or_unclear; not_mentioned; AJIO
- survey_r001_preferred_platform_footwear — irrelevant_or_unclear; not_mentioned; Myntra
- survey_r001_preferred_platform_accessories — irrelevant_or_unclear; not_mentioned; Other
- survey_r001_nykaa_fashion_usage_frequency — irrelevant_or_unclear; not_mentioned; Sometimes
- survey_r002_age_range — irrelevant_or_unclear; not_mentioned; 22–25

## Contradictory evidence

No contradiction should be declared from fallback labels alone. Reviewers should check cases where a respondent reports prior wishlist purchase but the most recent wishlisted item is still being considered, forgotten, abandoned, or unavailable. These may represent different episodes rather than logical errors.

## Candidate wishlist-specific barriers

These are hypotheses for human review, not validated barriers.

| Candidate theme | Records |
|---|---:|
| other/unclear | 68 |
| value/price assessment | 57 |
| wishlist/UX discoverability | 17 |
| occasion/styling | 12 |
| quality/material confidence | 9 |
| fit/size confidence | 7 |
| deprioritization/memory | 5 |
| comparison/alternative | 4 |
| availability/stock | 2 |
| review/product-information confidence | 1 |

## Human review requirements

- Review all direct_wishlist_behavior records.
- Review all HIGH-confidence records.
- Review all LOW-confidence and ambiguous records.
- Review HIGH-heuristic records classified as general, post-purchase, or unclear.
- Review every random control for keyword-filter bias.
- Record adjudicated labels and disagreement notes in human_review_queue.csv.

## Readiness

**Not ready to scale.** The taxonomy and workflow require an actual model run plus human review, especially because the browser engine was not executed, deterministic pre-labels are not AI classifications, public records lack stable provenance, and the current taxonomy does not natively encode evidence type or wishlist linkage.
