import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputPath = path.join(projectRoot, "mvp", "data", "nykaa_discovery_bundle.js");
const validationOutputPath = path.join(projectRoot, "analysis", "automated_validation_output.csv");

function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  const source = String(text).replace(/^\uFEFF/, "");
  for (let i = 0; i < source.length; i += 1) {
    const c = source[i];
    const next = source[i + 1];
    if (inQuotes) {
      if (c === '"' && next === '"') {
        field += '"';
        i += 1;
      } else if (c === '"') {
        inQuotes = false;
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else if (c !== "\r") {
      field += c;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  if (!rows.length) return [];
  const headers = rows.shift().map((header) => header.trim().toLowerCase());
  return rows
    .filter((current) => current.length > 1 || (current[0] && current[0].trim()))
    .map((current) => Object.fromEntries(headers.map((header, index) => [header, (current[index] ?? "").trim()])));
}

async function readRows(relativePath) {
  return parseCSV(await fs.readFile(path.join(projectRoot, relativePath), "utf8"));
}

const VALIDATION_METHOD = "deterministic source-text and survey-field validation; no LLM or network call";
const VALIDATION_VERSION = "automated-validation-v1";
const BARRIERS = [
  "value/price assessment",
  "fit/size confidence",
  "quality/material confidence",
  "review/product-information confidence",
  "trust/authenticity",
  "availability/stock",
  "comparison/alternative",
  "occasion/styling",
  "deprioritization/memory",
  "wishlist/UX discoverability",
];

function lower(value) {
  return String(value ?? "").trim().toLowerCase();
}

function has(text, pattern) {
  return pattern.test(text);
}

function fieldIsContextOnly(field) {
  if (/(wishlist|wish_list|saved_item|saved_items|last_wishlisted|purchase_barrier|purchase_trigger|one_thing_to_help_purchase)/.test(field)) return false;
  return /(^|_)(age|city|gender|email|name|platform|frequency|spend|category)(_|$)/.test(field);
}

function surveySemantics(field) {
  if (field === "purchase_likelihood") return { kind: "survey_context", label: "survey context / purchase-likelihood measurement" };
  if (field === "purchase_triggers") return { kind: "desired_trigger", label: "survey purchase trigger" };
  if (field === "purchase_barriers") return { kind: "reported_barrier", label: "survey reported barriers" };
  if (field === "last_wishlisted_product_outcome") return { kind: "wishlist_outcome", label: "wishlist outcome" };
  if (field === "one_thing_to_help_purchase_wishlist") return { kind: "requested_help", label: "requested product help" };
  if (/(wishlist|wish_list|saved_item|saved_items|purchased_after_wishlist|how_often_do_you_add_items_to_wishlist|how_often_do_you_purchase_items_from_wishlist)/.test(field)) return { kind: "wishlist_context", label: "wishlist behaviour/context" };
  return null;
}

function inferSignals(record) {
  const text = lower(record.raw_text);
  const field = lower(record.question_field);
  const semantics = lower(record.source_type) === "primary_research" ? surveySemantics(field) : null;
  const surveyFieldContext = lower(record.source_type) === "primary_research"
    && /(wishlist|wish_list|saved_item|saved_items|last_wishlisted|purchase_barrier|purchase_trigger|one_thing_to_help_purchase)/.test(field);
  const explicitWishlist = has(text, /\b(wishlist(?:ed|ing)?|wish list|saved item|saved items|save for later|bookmark(?:ed)?)\b/);
  const waiting = has(text, /\b(wait|waiting|later|consider(?:ing)?|thinking|decid(?:e|ed|ing)|not sure|unsure|didn'?t buy|did not buy|not purchased|depriorit)\b/);
  const postPurchase = has(text, /\b(deliver(?:y|ed)|received|return(?:ed)?|refund|damaged|defect(?:ive)?|wrong item|customer service|order issue|poor packaging)\b/);
  const genericContext = fieldIsContextOnly(field) || /^(email|name|timestamp)$/.test(field);
  const wishlistUx = explicitWishlist && has(text, /\b(disappear(?:s|ed|ing)?|remov(?:e|ed|ing)|load|view|see|show|save|saved|glitch|option|complete|not able|unable|cannot|can't|only\s+\d+)\b/);
  let evidenceType = "general_shopping_friction";
  let strength = "contextual";
  if (!text || genericContext || semantics?.kind === "survey_context") {
    evidenceType = "irrelevant_or_unclear";
    strength = "insufficient";
  } else if (semantics?.kind === "desired_trigger" || semantics?.kind === "reported_barrier") {
    evidenceType = "pre_purchase_hesitation";
    strength = "explicit_pre_purchase";
  } else if (semantics?.kind === "wishlist_outcome") {
    evidenceType = "direct_wishlist_behavior";
    strength = "direct";
  } else if (semantics?.kind === "requested_help") {
    evidenceType = explicitWishlist ? "direct_wishlist_behavior" : "pre_purchase_hesitation";
    strength = explicitWishlist ? "direct" : "explicit_pre_purchase";
  } else if (wishlistUx) {
    evidenceType = "direct_wishlist_behavior";
    strength = "direct";
  } else if (postPurchase) {
    evidenceType = "post_purchase_complaint";
    strength = "direct";
  } else if (surveyFieldContext && /(wishlist_item|wishlist_saved|purchased_after_wishlist|how_often_do_you_add_items_to_wishlist|how_often_do_you_purchase_items_from_wishlist)/.test(field)) {
    evidenceType = "direct_wishlist_behavior";
    strength = "direct";
  } else if (explicitWishlist && waiting) {
    evidenceType = "pre_purchase_hesitation";
    strength = "explicit_pre_purchase";
  } else if (surveyFieldContext && /(purchase_barrier|purchase_trigger)/.test(field)) {
    evidenceType = "pre_purchase_hesitation";
    strength = "explicit_pre_purchase";
  } else if (waiting || has(text, /\b(price|expensive|cost|size|fit|quality|review|rating|stock|alternative|compare)\b/)) {
    evidenceType = "pre_purchase_hesitation";
    strength = "explicit_pre_purchase";
  } else if (explicitWishlist || surveyFieldContext) {
    evidenceType = "direct_wishlist_behavior";
    strength = "direct";
  }
  return { text, field, semantics, explicitWishlist, surveyFieldContext, waiting, postPurchase, genericContext, wishlistUx, evidenceType, strength };
}

function themeNegated(text, theme) {
  const negations = {
    "availability/stock": /\b(?:not|isn't|isnt|is not)\s+(?:out of stock|unavailable)\b|\bnot\s+(?:because of|due to)\s+(?:product\s+)?(?:stock|availability)\b/,
    "value/price assessment": /\bnot\s+(?:because of|due to)\s+(?:the\s+)?(?:price|cost)\b|\bno issue with (?:the\s+)?price\b/,
    "fit/size confidence": /\bnot\s+(?:because of|due to)\s+(?:the\s+)?(?:size|fit)\b|\bno issue with (?:the\s+)?(?:size|fit)\b/,
    "quality/material confidence": /\bnot\s+(?:because of|due to)\s+(?:the\s+)?quality\b|\bno issue with (?:the\s+)?quality\b/,
  };
  return Boolean(negations[theme]?.test(text));
}

function inferBarriers(record, signal) {
  const text = signal.text;
  const semantics = signal.semantics?.kind;
  if (semantics === "survey_context" || semantics === "desired_trigger") return [];
  if (signal.wishlistUx) return ["wishlist/UX discoverability"];
  const rules = [
    ["availability/stock", /\b(out of stock|out-of-stock|never comes? in stock|unavailable|availability|size available|comes (?:back )?in stock|stock issue)\b/],
    ["fit/size confidence", /\b(unsure|uncertain|concern|doubt|size|fit|fitting|measurements?|sizing)\b/],
    ["quality/material confidence", /\b(quality concerns?|poor quality|cheap products?|does not match the (?:product )?description or quality|fabric|material|durab(?:le|ility)|stitching|used|damaged|damage)\b/],
    ["review/product-information confidence", /\b(no|lack of|missing|few|better|more)\s+(?:customer )?(?:reviews?|ratings?|photo|product information|details)|(?:reviews?|ratings?|description|product information|details).{0,35}\b(?:not|missing|lack|poor|bad|better|more)\b/],
    ["trust/authenticity", /\b(fake|authentic|genuine|trust|duplicate|fraud|scam)\b/],
    ["comparison/alternative", /\b(compare|comparing|alternative|elsewhere|another|myntra|ajio|amazon|similar product)\b/],
    ["occasion/styling", /\b(occasion|wedding|event|styling|outfit|inspiration)\b/],
    ["deprioritization/memory", /\b(forget|forgot|lost track|depriorit|discard|changed my mind)\b/],
    ["value/price assessment", /\b(price too high|too+ much cost|expensive|high price|not worth|better price|cheaper|afford|cost compare(?:d)?|price|discount|deal)\b/],
  ];
  const broadSemantics = ["reported_barrier", "requested_help", "wishlist_outcome"].includes(semantics);
  return rules.filter(([theme, rule]) => {
    if (!(rule.test(text) || (semantics === "requested_help" && theme === "review/product-information confidence" && /\b(review|rating|product information|details)\b/.test(text))) || themeNegated(text, theme)) return false;
    if (theme === "availability/stock" && /\b(?:customer|rider|delivery partner|at home|saying i was|home and)\b.{0,100}\b(?:unavailable|available)\b/.test(text) && !/\b(?:out of stock|in stock|stock|size available|product availability)\b/.test(text)) return false;
    if (!broadSemantics) {
      const problemSignal = /\b(concern|concerns|unsure|uncertain|doubt|problem|issue|difficult|hard|worr(?:y|ied)|not sure|didn'?t|did not|poor|bad|cheap|expensive|high price|cost|out of stock|unavailable|doesn'?t fit|does not fit|wrong|fake|duplicate|scam|fraud|forget|forgot|lost track|discard|changed my mind|not able|unable|cannot|can't|disappear|removed|load|used|damaged)\b/.test(text);
      if (!problemSignal && !["comparison/alternative", "availability/stock", "deprioritization/memory", "wishlist/UX discoverability"].includes(theme)) return false;
    }
    return true;
  }).map(([theme]) => theme);
}

function inferTriggerThemes(text) {
  const normalized = lower(text);
  const triggerRules = [
    ["value/price assessment", /\b(price|discount|deal|cheaper|cost|afford|value)\b/],
    ["fit/size confidence", /\b(size|fit|fitting|sizing|measurements?)\b/],
    ["quality/material confidence", /\b(quality|fabric|material|durab(?:le|ility))\b/],
    ["review/product-information confidence", /\b(reviews?|ratings?|product information|description|details)\b/],
    ["availability/stock", /\b(out of stock|in stock|stock|available|availability)\b/],
    ["comparison/alternative", /\b(compare|alternative|elsewhere|similar)\b/],
  ];
  return triggerRules.filter(([theme, rule]) => rule.test(normalized) && !themeNegated(normalized, theme)).map(([theme]) => theme);
}

function validateRecord(record) {
  const signal = inferSignals(record);
  const semantics = signal.semantics;
  const candidateType = String(record.evidence_type || "irrelevant_or_unclear").trim();
  const candidateLink = String(record.wishlist_link || "not_mentioned").trim();
  const candidateIntent = String(record.primary_intent || "unknown").trim();
  const candidateJourney = String(record.journey_stage || "unknown").trim();
  const candidateBarrier = String(record.barrier_theme || "other/unclear").trim();
  const inferredBarriers = inferBarriers(record, signal);
  const inferredTriggerThemes = semantics?.kind === "desired_trigger" ? inferTriggerThemes(signal.text) : [];
  let status = "automatically_validated";
  let validatedType = candidateType;
  let validatedLink = candidateLink;
  let validatedIntent = candidateIntent;
  let validatedJourney = candidateJourney;
  let validatedBarrier = candidateBarrier;
  let support = "candidate fields are consistent with available source text/field context";
  let rationale = "No unsupported barrier or wishlist linkage detected by deterministic checks.";
  let validatedOutcome = String(record.outcome_signal || "unknown").trim() || "unknown";

  if (semantics?.kind === "survey_context") {
    validatedType = "irrelevant_or_unclear";
    validatedLink = "not_mentioned";
    validatedIntent = "unknown";
    validatedJourney = "unknown";
    validatedBarrier = "other/unclear";
    status = candidateType === validatedType && candidateBarrier === validatedBarrier ? "automatically_validated" : "automatically_corrected";
    rationale = "Survey purchase-likelihood value is retained as context/intent measurement, not shopping-friction evidence or a barrier.";
  } else if (semantics?.kind === "desired_trigger") {
    validatedType = "pre_purchase_hesitation";
    validatedLink = "not_mentioned";
    validatedIntent = "unknown";
    validatedJourney = "pre_purchase";
    validatedBarrier = "other/unclear";
    status = candidateType === validatedType && candidateLink === validatedLink && candidateBarrier === validatedBarrier ? "automatically_validated" : "automatically_corrected";
    support = "response describes desired purchase triggers, not observed barrier behaviour";
    rationale = `Survey purchase-trigger response is retained as a desired trigger (${inferredTriggerThemes.join(", ") || "no mapped theme"}) and excluded from observed-barrier and wishlist-causality counts.`;
  } else if (!signal.text) {
    validatedType = "irrelevant_or_unclear";
    validatedLink = "not_mentioned";
    validatedIntent = "unknown";
    validatedJourney = "unknown";
    validatedBarrier = "other/unclear";
    status = "ambiguous_needs_review";
    support = "source text is blank";
    rationale = "Blank source evidence cannot support a behavioural or barrier classification.";
  } else if (signal.evidenceType !== candidateType) {
    status = "automatically_corrected";
    validatedType = signal.evidenceType;
    rationale = `Source text/field context supports ${signal.evidenceType}; candidate evidence type was ${candidateType}.`;
  }

  if (semantics?.kind === "desired_trigger" || semantics?.kind === "survey_context") {
    validatedLink = "not_mentioned";
  } else if (semantics?.kind === "reported_barrier") {
    validatedLink = "explicit_pre_purchase";
  } else if (semantics?.kind === "wishlist_outcome") {
    validatedLink = "explicit_direct";
  } else if (semantics?.kind === "requested_help") {
    validatedLink = signal.explicitWishlist ? "explicit_direct" : "explicit_pre_purchase";
  } else if (!signal.explicitWishlist && !signal.surveyFieldContext && ["explicit_direct", "explicit_pre_purchase"].includes(candidateLink)) {
    status = "automatically_corrected";
    validatedLink = "not_mentioned";
    rationale = `${rationale} No explicit wishlist/saved-item signal is present in the source text.`;
  } else if (signal.explicitWishlist || signal.surveyFieldContext) {
    validatedLink = signal.waiting && validatedType === "pre_purchase_hesitation" ? "explicit_pre_purchase" : "explicit_direct";
  }
  if (validatedLink !== candidateLink && !["survey_context", "desired_trigger"].includes(semantics?.kind)) {
    status = "automatically_corrected";
    rationale = `${rationale} Wishlist linkage was set from explicit source/field semantics.`;
  }
  if (signal.postPurchase && !signal.explicitWishlist && candidateLink !== "not_mentioned") {
    validatedLink = "not_mentioned";
    status = "automatically_corrected";
    rationale = `${rationale} Post-purchase complaints are not treated as wishlist causality without an explicit wishlist signal.`;
  }
  if (validatedType === "pre_purchase_hesitation" && !["desired_trigger", "survey_context"].includes(semantics?.kind)) validatedIntent = "considering_or_waiting";
  if (semantics?.kind === "wishlist_outcome") validatedJourney = "wishlist_revisit";
  else if (validatedType === "direct_wishlist_behavior") validatedJourney = candidateJourney === "unknown" || candidateJourney === "context" ? "wishlist_revisit" : candidateJourney;
  else if (validatedType === "pre_purchase_hesitation") validatedJourney = "pre_purchase";
  else if (validatedType === "post_purchase_complaint") validatedJourney = "post_purchase";
  else if (validatedType === "general_shopping_friction") validatedJourney = "general_shopping";
  else if (validatedType === "irrelevant_or_unclear") validatedJourney = "unknown";

  let validatedBarriers = inferredBarriers;
  if (semantics?.kind === "survey_context" || semantics?.kind === "desired_trigger") validatedBarriers = [];
  if (validatedBarriers.length) {
    validatedBarrier = validatedBarriers.includes(candidateBarrier) ? candidateBarrier : validatedBarriers[0];
    if (candidateBarrier !== validatedBarrier || candidateBarrier === "other/unclear") {
      status = "automatically_corrected";
      rationale = `${rationale} Source text/field semantics support: ${validatedBarriers.join(", ")}.`;
    }
  } else if (candidateBarrier !== "other/unclear") {
    status = "automatically_corrected";
    validatedBarrier = "other/unclear";
    support = "candidate barrier is not supported by the source text/field semantics";
    rationale = `The candidate barrier ${candidateBarrier} was removed because the source does not support it; no replacement barrier was invented.`;
  }
  if (semantics?.kind === "wishlist_outcome") {
    if (/\b(similar product elsewhere|elsewhere|alternative)\b/.test(signal.text)) validatedOutcome = "alternative_purchase";
    else if (/\b(out of stock|unavailable|not available)\b/.test(signal.text) && !themeNegated(signal.text, "availability/stock")) validatedOutcome = "unavailable_or_out_of_stock";
    else if (/\b(consider|waiting|later)\b/.test(signal.text)) validatedOutcome = "considering_or_waiting";
    else if (/\b(bought|purchased|yes)\b/.test(signal.text)) validatedOutcome = "purchased";
  }
  if (signal.genericContext && candidateType !== "irrelevant_or_unclear") {
    status = "automatically_corrected";
    validatedType = "irrelevant_or_unclear";
    validatedLink = "not_mentioned";
    validatedBarrier = "other/unclear";
    validatedBarriers = [];
    validatedJourney = "unknown";
    validatedIntent = "unknown";
    rationale = "Survey context field is retained for segmentation only; it is not treated as behavioural evidence.";
  }
  if (!signal.text) {
    validatedLink = "not_mentioned";
    validatedBarriers = [];
  }
  const observedBarrier = validatedBarriers.length > 0 && !["desired_trigger", "requested_help", "survey_context"].includes(semantics?.kind);
  const validatedInclude = observedBarrier && ["direct_wishlist_behavior", "pre_purchase_hesitation"].includes(validatedType) && ["explicit_direct", "explicit_pre_purchase"].includes(validatedLink) ? "yes" : "no";
  if (semantics?.kind === "requested_help") rationale = `${rationale} Requested help is retained as qualitative context, not counted as an observed barrier without separate behavioural evidence.`;
  return {
    automated_validation_status: status,
    validated_evidence_type: validatedType,
    validated_wishlist_link: validatedLink,
    validated_primary_intent: validatedIntent,
    validated_journey_stage: validatedJourney,
    validated_barrier_theme: validatedBarrier,
    validated_barriers: validatedBarriers,
    validated_outcome_signal: validatedOutcome,
    validated_trigger_themes: inferredTriggerThemes,
    evidence_subtype: semantics?.kind || (validatedType === "post_purchase_complaint" ? "post_purchase_complaint" : validatedBarriers.length ? "observed_barrier" : "general_context"),
    theme_signal_type: semantics?.kind === "desired_trigger" ? "desired_trigger" : semantics?.kind === "requested_help" ? "requested_help" : semantics?.kind === "survey_context" ? "survey_context" : validatedBarriers.length ? "observed_barrier" : "no_specific_theme",
    validated_include_in_quantitative_analysis: validatedInclude,
    evidence_support: support,
    validation_rationale: rationale,
    validation_confidence: status === "ambiguous_needs_review" ? "low" : signal.strength === "insufficient" ? "low" : "medium",
    validation_method: VALIDATION_METHOD,
    validation_version: VALIDATION_VERSION,
  };
}

function escapeCSV(value) {
  const serialized = Array.isArray(value) ? JSON.stringify(value) : String(value ?? "");
  return `"${serialized.replaceAll("\"", "\"\"")}"`;
}

function writeCSV(rows) {
  const extra = [
    "automated_validation_status", "validated_evidence_type", "validated_wishlist_link", "validated_primary_intent", "validated_journey_stage", "validated_barrier_theme", "validated_barriers", "validated_outcome_signal", "validated_trigger_themes", "evidence_subtype", "theme_signal_type", "validated_include_in_quantitative_analysis", "evidence_support", "validation_rationale", "validation_confidence", "validation_method", "validation_version",
  ];
  const headers = [...new Set([...Object.keys(rows[0] || {}), ...extra])];
  return [headers.join(","), ...rows.map((row) => headers.map((header) => escapeCSV(row[header])).join(","))].join("\n") + "\n";
}

const bundle = {
  pilot_dataset: await readRows("data/processed/pilot/pilot_dataset.csv"),
  classification_output: await readRows("data/processed/pilot/classification_output.csv"),
  human_adjudication: await readRows("human_adjudication.csv"),
};

for (const [name, rows] of Object.entries(bundle)) {
  if (!rows.length) throw new Error(`${name} produced no rows`);
  const ids = rows.map((row) => row.record_id).filter(Boolean);
  if (ids.length !== new Set(ids).size) throw new Error(`${name} contains duplicate record IDs`);
}

const classificationIds = new Set(bundle.classification_output.map((row) => row.record_id));
for (const name of ["pilot_dataset", "human_adjudication"]) {
  const ids = new Set(bundle[name].map((row) => row.record_id));
  if (ids.size !== classificationIds.size || [...classificationIds].some((id) => !ids.has(id))) {
    throw new Error(`${name} and classification_output do not contain the same record IDs`);
  }
}

const pilotById = new Map(bundle.pilot_dataset.map((row) => [row.record_id, row]));
const humanById = new Map(bundle.human_adjudication.map((row) => [row.record_id, row]));
const automatedValidation = bundle.classification_output.map((row) => {
  const provenance = pilotById.get(row.record_id) || {};
  const human = humanById.get(row.record_id) || {};
  const base = { ...provenance, ...row };
  const validation = validateRecord(base);
  return {
    ...base,
    human_review_status: human.human_review_status || row.human_review_status || "pending",
    human_label: human.human_label || row.human_label || "",
    human_evidence_type: human.human_evidence_type || "",
    human_wishlist_link: human.human_wishlist_link || "",
    human_primary_intent: human.human_primary_intent || "",
    human_journey_stage: human.human_journey_stage || "",
    human_barrier_theme: human.human_barrier_theme || "",
    human_include_in_quantitative_analysis: human.human_include_in_quantitative_analysis || "",
    human_decision: human.human_decision || "",
    human_verified: human.human_verified || "",
    human_verified_at: human.human_verified_at || "",
    reviewed_at: human.reviewed_at || "",
    reviewer_notes: human.reviewer_notes || "",
    ...validation,
  };
});
if (automatedValidation.length !== bundle.classification_output.length) throw new Error("automated validation output row count does not match classification output");
const validationIds = new Set(automatedValidation.map((row) => row.record_id).filter(Boolean));
if (validationIds.size !== classificationIds.size || [...classificationIds].some((id) => !validationIds.has(id))) throw new Error("automated validation output and classification output do not contain the same record IDs");
bundle.automated_validation_output = automatedValidation;

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(path.dirname(validationOutputPath), { recursive: true });
const contents = `/* Generated from the existing CSV source-of-truth files. Do not edit manually. */\nwindow.NYKAA_DISCOVERY_BUNDLE = ${JSON.stringify(bundle)};\n`;
await fs.writeFile(outputPath, contents, "utf8");
await fs.writeFile(validationOutputPath, writeCSV(automatedValidation), "utf8");
const validationCounts = Object.fromEntries([...new Set(automatedValidation.map((row) => row.automated_validation_status))].map((status) => [status, automatedValidation.filter((row) => row.automated_validation_status === status).length]));
console.log(JSON.stringify({ output: path.relative(projectRoot, outputPath), validation_output: path.relative(projectRoot, validationOutputPath), rows: Object.fromEntries(Object.entries(bundle).map(([name, rows]) => [name, rows.length])), validation_counts: validationCounts }));
