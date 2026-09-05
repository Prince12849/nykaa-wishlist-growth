# Discovery Engine pilot validation

This report was generated from `data/processed/pilot/classification_output.csv` using the v2 browser-layer candidate rules. It is a technical/data-contract validation, not human adjudication and not a final research conclusion.

## Coverage and governance checks

- Pilot records processed: **365**
- Required columns missing: **none**
- Duplicate record IDs: **0**
- Records with `human_review_status=pending`: **365/365**
- Non-empty `human_label` values: **0** (must remain 0 until adjudication)
- Candidate wishlist-linked direct/pre-purchase records: **109**
- Human agreement, accuracy, and validation metrics: **not computed**

## Funnel counts

| Stage | Count |
|---|---:|
| Research | 365 |
| Relevance (raw text plus source/relevance context) | 363 |
| Evidence type | 365 |
| Journey stage | 365 |
| Wishlist linkage | 365 |
| Primary intent (available or conservatively mapped) | 24 |
| Outcome | 365 |
| Barrier | 365 |
| Trigger | 365 |
| User context/segment fields captured | 300 |
| Evidence strength/confidence | 365 |
| Candidate cross-source patterns | 3 |
| Candidate patterns | 9 |
| Candidate problem hypotheses | 9 |

## Counts by source

| Source | Records |
|---|---:|
| `survey` | 300 |
| `Play Store` | 53 |
| `App Store` | 12 |

## Counts by evidence type

| Evidence type | Records |
|---|---:|
| `irrelevant_or_unclear` | 140 |
| `direct_wishlist_behavior` | 97 |
| `pre_purchase_hesitation` | 86 |
| `post_purchase_complaint` | 39 |
| `general_shopping_friction` | 3 |

## Counts by journey stage

| Journey stage | Records |
|---|---:|
| `context` | 139 |
| `pre_purchase` | 86 |
| `wishlist_behavior` | 60 |
| `post_purchase` | 39 |
| `post_wishlist_outcome` | 20 |
| `wishlist_behavior_or_revisit` | 17 |
| `general_shopping` | 3 |
| `unknown` | 1 |

## Counts by wishlist linkage

| Wishlist linkage | Records |
|---|---:|
| `not_mentioned` | 177 |
| `explicit_direct` | 102 |
| `explicit_pre_purchase` | 80 |
| `inferred_or_ambiguous` | 6 |

## Theme distribution by source

### App Store

| Barrier theme | Records |
|---|---:|
| `availability/stock` | 3 |
| `other/unclear` | 3 |
| `review/product-information confidence` | 2 |
| `trust/authenticity` | 2 |
| `quality/material confidence` | 1 |
| `value/price assessment` | 1 |

### Play Store

| Barrier theme | Records |
|---|---:|
| `wishlist/UX discoverability` | 17 |
| `other/unclear` | 14 |
| `value/price assessment` | 7 |
| `quality/material confidence` | 4 |
| `availability/stock` | 3 |
| `fit/size confidence` | 3 |
| `trust/authenticity` | 3 |
| `review/product-information confidence` | 1 |
| `comparison/alternative` | 1 |

### survey

| Barrier theme | Records |
|---|---:|
| `other/unclear` | 208 |
| `value/price assessment` | 53 |
| `occasion/styling` | 12 |
| `quality/material confidence` | 9 |
| `fit/size confidence` | 6 |
| `deprioritization/memory` | 5 |
| `comparison/alternative` | 3 |
| `wishlist/UX discoverability` | 3 |
| `availability/stock` | 1 |

## Heuristic relevance versus candidate classification

| Heuristic relevance | Evidence type | Records |
|---|---|---:|
| `` | `direct_wishlist_behavior` | 80 |
| `` | `irrelevant_or_unclear` | 140 |
| `` | `pre_purchase_hesitation` | 80 |
| `HIGH` | `direct_wishlist_behavior` | 17 |
| `HIGH` | `post_purchase_complaint` | 11 |
| `HIGH` | `pre_purchase_hesitation` | 1 |
| `LOW` | `general_shopping_friction` | 2 |
| `LOW` | `post_purchase_complaint` | 21 |
| `LOW` | `pre_purchase_hesitation` | 5 |
| `MEDIUM` | `general_shopping_friction` | 1 |
| `MEDIUM` | `post_purchase_complaint` | 7 |

The table describes deterministic pilot labels; it does not establish that the heuristic or the classification is correct.

## Potential keyword-filter false positives

These are review-priority examples where HIGH/MEDIUM heuristic relevance co-occurs with a contextual or unclear candidate evidence type. They are not confirmed false positives until human review.

| Record ID | Source | Heuristic | Candidate type | Raw text excerpt |
|---|---|---|---|---|
| `play_store_f136d042eb56940f` | Play Store | HIGH | post_purchase_complaint | While proceeding to payment for first order I couldn't avail the '10% off on first order' The products went out of stock while placing the order, though the stock was seen availabl |
| `play_store_a609a7ba9d01ff00` | Play Store | HIGH | post_purchase_complaint | Very faulty app. Unlike the nykaa beauty app this app is not user friendly. There is a problem in saving items to your wishlist it just does not get saved! In fact on their website |
| `play_store_ad201146d6bc3212` | Play Store | HIGH | post_purchase_complaint | Customer support was excellent. I was in search for an item but couldn't find it. I went to the chat box and Stephanie from customer support helped me out instantly and saved my ti |
| `play_store_a97f7fa4d9edf0c1` | Play Store | HIGH | post_purchase_complaint | prices and cloth ranges are good but if i wishlist something for later it ends up either getting stocked out and never returns back in stock for months |
| `play_store_317de7fc102e81fc` | Play Store | HIGH | post_purchase_complaint | First I add many items in cart,when I want to buy one thing from cart,,I have no option to buy just one thing from cart,,so I move to wishlist all items,after I order that selected |
| `play_store_1548a35ad245ff5a` | Play Store | HIGH | post_purchase_complaint | Great collection, but zero customer support. I've been waiting for my refund from nykaa fashion from past 11 days now but no response from their side 😒. And all this in the times w |
| `app_store_13ff23104d857eff` | App Store | HIGH | post_purchase_complaint | I received my order on time, but when I wanted to return it, the process took far too long and required multiple attempts. The delivery partner did not even call me, yet they false |
| `app_store_2a90097a9524966b` | App Store | HIGH | post_purchase_complaint | this is totally a fake application...and i believe all the positive reviews are paid. O am struggling a lot with my first time order. they have sent me the incomplete product where |
| `play_store_f6a18504af3b1de9` | Play Store | MEDIUM | post_purchase_complaint | As a customer, I paid for my order and trusted Nykaa Fashion to provide reliable service. Instead, I have been left waiting without any proper explanation or resolution. Every day  |
| `app_store_5603bad54651a846` | App Store | MEDIUM | post_purchase_complaint | i literally ordered shoes from aldo and got delivered fake products worst app over do not buy branded stuff they will loot you and won’t even give money not even arrange for pickup |
| `play_store_31b4c4a120629eb6` | Play Store | MEDIUM | post_purchase_complaint | This is such a worst and bad online store. My first order, among two I placed return request for one. But after raising return request, it's been ages since I made request. No one  |
| `play_store_006f5ab2619a83df` | Play Store | HIGH | post_purchase_complaint | Worse e commerce site in service.His Logistics partner is not responsible and Nykaa CC is not able reply any thing regarding delivery. CC can not take follow up with courrier partn |
| `app_store_a94173218c9a5600` | App Store | HIGH | post_purchase_complaint | The worst app when it comes to exchange or return. I had my exchange item been waiting for a week to be picked up and neither is the chat not is the customer care responsive . Also |
| `app_store_c3c612147fc72ab1` | App Store | HIGH | post_purchase_complaint | 1-day delivery turned into 4 days, and I’m still waiting for my order. This has been an incredibly frustrating experience. I’ll definitely think twice before using this app again. |
| `play_store_f3f6cb96dc0283af` | Play Store | MEDIUM | post_purchase_complaint | Worst experience with Nykaa. I returned a product as it did not fit. Delhivery picked it up, but the app showed “pickup unsuccessful due to Sl. no mismatch.” After multiple emails  |
| `play_store_ad84ed596b5f8f68` | Play Store | MEDIUM | post_purchase_complaint | Very bad pathetic disgusting please it's my humble req don't buy any product from this site bcoz they send wrong product and wen u want to return no one come and all customer care  |
| `app_store_9b37bf5165295526` | App Store | MEDIUM | post_purchase_complaint | The most of the fashion brands available on the app quite high prices but offer cheap products which do not match the product description or quality. I have even had an entirely di |
| `app_store_2cdd7190aebd98de` | App Store | MEDIUM | post_purchase_complaint | Nykaa fashion’s vendors are selling totally duplicate products with no return or replacement policy. I would recommend to not buy products from nykaa fashion. They are not authenti |

## Candidate wishlist-specific barriers

The following are candidate pattern rows produced by the funnel rule: explicit wishlist linkage, direct/pre-purchase evidence type, included record, and non-unclear barrier. Every row remains pending human review.

| Candidate theme | Records | Sources | Status | Trace IDs |
|---|---:|---|---|---|
| value/price assessment | 53 | survey | HYPOTHESIS — pending human review | `survey_r001_purchase_barriers, survey_r001_purchase_triggers, survey_r002_wishlist_item_types, survey_r002_purchase_barriers, survey_r002_purchase_triggers, survey_r004_wishlist_item_types, survey_r004_purchase_barriers, survey_r004_purchase_triggers` |
| wishlist/UX discoverability | 17 | Play Store, survey | HYPOTHESIS — pending human review | `survey_r009_one_thing_to_help_purchase_wishlist, survey_r014_one_thing_to_help_purchase_wishlist, survey_r015_purchase_triggers, play_store_188cce47d0928c65, play_store_e3720bd2679247e8, play_store_61df229f45c06b1f, play_store_3a29e2045f462495, play_store_2c1c1787191df1c1` |
| occasion/styling | 12 | survey | HYPOTHESIS — pending human review | `survey_r001_purchased_after_wishlist, survey_r002_purchased_after_wishlist, survey_r003_purchased_after_wishlist, survey_r004_purchased_after_wishlist, survey_r005_purchased_after_wishlist, survey_r006_purchased_after_wishlist, survey_r007_purchased_after_wishlist, survey_r010_purchased_after_wishlist` |
| quality/material confidence | 9 | survey | HYPOTHESIS — pending human review | `survey_r001_wishlist_item_types, survey_r003_wishlist_item_types, survey_r006_wishlist_item_types, survey_r011_wishlist_item_types, survey_r012_wishlist_item_types, survey_r013_wishlist_item_types, survey_r015_wishlist_item_types, survey_r019_wishlist_item_types` |
| fit/size confidence | 7 | Play Store, survey | HYPOTHESIS — pending human review | `survey_r002_one_thing_to_help_purchase_wishlist, survey_r003_purchase_barriers, survey_r003_purchase_triggers, survey_r008_purchase_triggers, survey_r017_purchase_triggers, survey_r019_purchase_triggers, play_store_9a6bc1a8d57100b7` |
| deprioritization/memory | 5 | survey | HYPOTHESIS — pending human review | `survey_r006_last_wishlisted_product_outcome, survey_r006_purchase_barriers, survey_r009_last_wishlisted_product_outcome, survey_r010_last_wishlisted_product_outcome, survey_r019_last_wishlisted_product_outcome` |
| comparison/alternative | 3 | survey | HYPOTHESIS — pending human review | `survey_r002_last_wishlisted_product_outcome, survey_r003_one_thing_to_help_purchase_wishlist, survey_r019_purchase_barriers` |
| availability/stock | 2 | Play Store, survey | HYPOTHESIS — pending human review | `survey_r016_last_wishlisted_product_outcome, play_store_e1126b7ea5e2cb0a` |
| review/product-information confidence | 1 | Play Store | HYPOTHESIS — pending human review | `play_store_23016bbd85b74a11` |

## Ambiguous/unclear records

- Records selected for review under the conservative ambiguity rule: **146**.
- No ambiguous record was recoded or excluded by this validation script.

## Contradictory evidence

No contradiction claim is made. The pilot has candidate labels only, no human adjudication, and no explicit contradiction-resolution protocol. Reviewers should compare direct/pre-purchase records against contextual/post-purchase records without treating the latter as wishlist causality.

## Human review required

- Review all direct wishlist records and the random controls in `human_review_queue.csv`.
- Adjudicate evidence type, wishlist linkage, barrier theme, confidence, and include/exclude status.
- Record human labels in a separate review artifact; do not overwrite candidate labels or populate review fields automatically.
- Recompute patterns and cross-source checks only after adjudication.
