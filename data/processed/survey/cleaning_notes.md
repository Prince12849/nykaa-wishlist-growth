# Survey Cleaning Notes

Audit and cleaning date: 2 September 2026 (IST)

## Source

The supplied path named an `.xlsx` file, but the file actually present and used is:

`data/raw/survey/Fashion Shopping & Wishlist Preferences (Responses) - Form responses 1.csv`

The raw CSV was read only and was not modified. Because the source is CSV, it has no worksheet names, workbook formatting, formulas, or duplicate-sheet structure.

## Counts

- Source format: CSV, not XLSX.
- Source table size including header: 21 rows × 17 columns.
- Original response count: 20.
- Cleaned response count: 20.
- Duplicate full response rows: 0.
- Cleaned output sheet: `survey_responses`.
- Cleaned output table size including header: 21 rows × 17 columns.

## Transformations performed

1. Preserved all 20 response rows in their original order. No response was added, removed, inferred, or rewritten.
2. Renamed the 17 headers to lowercase `snake_case` names using the mapping below. Header-only trailing spaces were removed as part of standardization.
3. Trimmed leading and trailing whitespace from every non-blank cell.
4. Converted blank cells to blank spreadsheet cells (`null`), without filling or imputing values.
5. In the three multi-select columns only, split the existing comma-separated selections, trimmed each selection, and rejoined them using `; ` so individual options remain auditable. No option was removed, reordered, corrected, or truncated—even where a respondent selected more than the stated limit.
6. Kept timestamps as text in their original `dd/mm/yyyy hh:mm:ss` representation; no timezone or date meaning was inferred.
7. Kept open-ended responses intact apart from leading/trailing whitespace trimming.
8. Kept the empty `email_address` column to preserve the source schema. No email values were added.
9. Added a table, filterable header, frozen header row, wrapping, and readable column widths to the cleaned workbook. These are presentation changes only and do not change response content.

## Column mapping

| Original column | Cleaned column |
|---|---|
| Timestamp | `timestamp` |
| Age | `age_range` |
| Current city | `current_city` |
| How often do you shop for fashion products online? | `online_fashion_shopping_frequency` |
| Which platform do you usually prefer for each category? [Clothing] | `preferred_platform_clothing` |
| Which platform do you usually prefer for each category? [Footwear] | `preferred_platform_footwear` |
| Which platform do you usually prefer for each category? [Accessories] | `preferred_platform_accessories` |
| How often do you use Nykaa Fashion? | `nykaa_fashion_usage_frequency` |
| Do you use wishlist or saved-items features on fashion apps? | `wishlist_saved_items_usage` |
| What do you usually add to your wishlist? (Select all that apply) | `wishlist_item_types` |
| Have you ever purchased a fashion product after adding it to your wishlist?  | `purchased_after_wishlist` |
| Think about the last fashion product you added to a wishlist. What happened next?  | `last_wishlisted_product_outcome` |
| What usually stops you from purchasing a wishlisted product? (Select up to 3) | `purchase_barriers` |
| When you add a product to your wishlist, how likely are you to purchase it? | `purchase_likelihood` |
| What would most likely make you purchase a wishlisted product? (Select up to 3) | `purchase_triggers` |
| If a fashion shopping app could do ONE thing to help you purchase wishlist products, what would you want it to do? | `one_thing_to_help_purchase_wishlist` |
| Email address | `email_address` |

## Missing-value summary

| Original column | Blank responses |
|---|---:|
| Timestamp | 0 |
| Age | 0 |
| Current city | 1 |
| Online fashion shopping frequency | 0 |
| Preferred platform: Clothing | 0 |
| Preferred platform: Footwear | 0 |
| Preferred platform: Accessories | 0 |
| Nykaa Fashion usage frequency | 0 |
| Wishlist/saved-items usage | 0 |
| Wishlist item types | 0 |
| Purchased after wishlist | 0 |
| Last wishlisted product outcome | 0 |
| Purchase barriers | 0 |
| Purchase likelihood | 0 |
| Purchase triggers | 0 |
| One thing to help purchase wishlist | 1 |
| Email address | 20 |

## Unique categorical values after whitespace trimming

- `age_range`: `26–30`; `22–25`
- `current_city`: `Bangalore`; `Hyderabad`; `Gurgaon`; `Delhi`; `Asansol`; `Prayagraj`; `Patna`; `Kanpur Nagar`; `Purnia`; `Patna city`; `Gurugram`; blank; `Noida`; `Ggn`; `banglore`; `Jaipur`
- `online_fashion_shopping_frequency`: `Every 2–3 months`; `Multiple times a month`; `About once a month`; `A few times a year`; `Rarely`
- `preferred_platform_clothing`: `AJIO`; `Myntra`; `Amazon`; `Nykaa Fashion`
- `preferred_platform_footwear`: `Myntra`; `Other`; `Amazon`; `I do not shop online for this`
- `preferred_platform_accessories`: `Other`; `Myntra`; `Amazon`; `I do not shop online for this`; `Nykaa Fashion`
- `nykaa_fashion_usage_frequency`: `Sometimes`; `Rarely`; `Used before but do not use now`; `Never used`; `Frequently`
- `wishlist_saved_items_usage`: `Sometimes`; `Frequently`; `Rarely`; `Never`
- `purchased_after_wishlist`: `Yes, occasionally`; `Yes, frequently`; `Rarely`
- `last_wishlisted_product_outcome`: `I am still considering purchasing it`; `I bought a similar product elsewhere`; `I purchased it`; `I don't remember`; `I decided not to buy it`; `It became unavailable/out of stock`
- `purchase_likelihood`: `1`; `2`; `3`; `4`

## Unique multi-select options after trimming

- `wishlist_item_types`: `Clothing`; `Footwear`; `Products I may buy later`; `Products waiting for a discount`; `Products I am comparing`; `Products for inspiration`; `Accessories`
- `purchase_barriers`: `Price too high`; `Waiting for discount`; `Comparing alternatives`; `Found a better product elsewhere`; `Unsure about size or fit`; `Quality concerns`; `Out of stock`; `Changed my mind`; `Waiting for an occasion`; `Forgot about it`
- `purchase_triggers`: `Price drop`; `Bigger discount`; `Better reviews or ratings`; `Better size or fit information`; `Better product information`; `Customer photos or videos`; `My preferred size becomes available`; `Styling suggestions`; `Back-in-stock notification`; `Easier returns`; `Faster delivery`

## Obvious data-quality issues retained for audit

- Eight of 20 responses selected more than three purchase barriers despite the “select up to 3” instruction; the maximum was six. All selected options were retained.
- Seven of 20 responses selected more than three purchase triggers despite the “select up to 3” instruction; the maximum was five. All selected options were retained.
- The city field contains unstandardized aliases/casing/spelling such as `Gurgaon`, `Gurugram`, `Ggn`, `Bangalore`, and `banglore`, plus `Patna city`. These were not semantically normalized because doing so could rewrite respondent meaning.
- The raw headers for the purchase-history and last-wishlisted-outcome questions contained trailing spaces; the cleaned headers do not.
- Leading/trailing whitespace occurred in city values and several open-ended responses. Only the outer whitespace was removed.
- One current-city response and one open-ended “one thing” response are blank. All 20 email fields are blank.
- Some open-ended text contains respondent wording/typos, including `galive`; these were preserved.
- Several open-ended responses mention discounts or free items even though the business constraint disallows monetary incentives. Those are respondent answers and were preserved; they are not product decisions or validated findings.

This file documents cleaning only. It does not perform product analysis, classification, problem definition, or solution selection.
