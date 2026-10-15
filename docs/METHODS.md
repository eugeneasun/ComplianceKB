# Methods and interpretation

## Knowledge representation and agent

An RKO groups the requirement frame, applicability, provenance and operational semantics:

`RKO = <r, A, P, O>`, where `r` contains the requirement and modality, `A` describes scope, `P` links the source and review metadata, and `O` contains trigger, evidence and verification method.

The released implementation retrieves records, assembles a prompt and output schema, and makes one bounded model call. `research/benchmark/run_llm_benchmark.py` contains the exact `official_entry`, `rkm_entry`, `build_context`, `build_prompt` and `answer_schema` functions. It returns requirement IDs, trigger/evidence labels, citations, one decision, rationale and missing-information/escalation explanation. The offline demo displays BM25 retrieval results only and does not simulate a model decision.

Decision options are `answer`, `need_more_information`, and `human_escalation`. These are reference policy decisions for synthetic scenarios, not verified conclusions that a real facility complies with law.

## Controlled inputs

The five conditions are all stored excerpts (`raw_full`), BM25, MiniLM dense retrieval, BM25/MiniLM hybrid, and RKM (`rkm_agent`). Hybrid and RKM use exactly the same candidate IDs; RKM includes additional curated fields. Both models use the same decision policy and output schema. Gold answer columns are excluded from prompts, while sharing the label taxonomy is an acknowledged evaluation dependency.

BM25 uses `k1=1.5`, `b=0.75`. Dense retrieval uses `sentence-transformers/all-MiniLM-L6-v2`, L2 normalization and exact dot-product ranking. Each component supplies up to 20 candidates. Fusion scores each record as:

`RRF(d) = sum_s 1 / (60 + rank_s(d))`

An absent rank contributes zero; ten records are retained after fusion. Post-hoc `intfloat/e5-base-v2` and BM25/E5 results are retrieval-only sensitivity checks, not an additional LLM experiment. Its recorded revision is `f52bf8ec8c7124536f0efb74aca902b2995e5bcd`.

## Scoring and uncertainty

Requirement IDs, citations, triggers and evidence are compared as sets. Per-scenario F1 is `2 * |G intersect P| / (|G| + |P|)`, then averaged across 24 scenarios. Both sets empty score 1; exactly one empty set scores 0. For example, 3 overlaps among 4 reference IDs and 5 predictions give `6/9 = 0.667`.

Decision accuracy is exact label agreement. Recall@10 measures recovery of relevant requirement IDs; MRR@10 rewards the first relevant rank; nDCG@10 rewards the placement of all relevant IDs. See `evaluate_benchmark.py` for exact conventions.

RKM-minus-hybrid differences use paired resampling over the same 24 scenario rows: 10,000 bootstrap resamples, seed 20260927, percentile 95% intervals. These intervals are exploratory uncertainty summaries for this development set. They do not correct for all multiple comparisons or remove dataset dependence.

Nominal Cohen's kappa is `(observed agreement - chance agreement) / (1 - chance agreement)`. All three annotation fields use nominal scoring, including risk; do not reinterpret the reported .234 as weighted ordinal kappa. Annotation bootstraps use 10,000 samples and seed 20260928.

## What the results support

On this development set, RKM has higher trigger and evidence F1 than hybrid for both models; their paired intervals exclude zero. Requirement and citation gains are not consistent, and decision accuracy is unchanged. Improved recovery of curated operational labels is a useful result, but does not show calibrated confidence or legal correctness.

## Sources of circularity and leakage risk

1. AI-assisted scenarios and reference labels use the same conceptual taxonomy as the knowledge model.
2. Scenarios were author-confirmed, not produced by a separate independent benchmark team; there is no independent holdout.
3. RKM supplies curated operational fields that the task asks the model to recover. That is the treatment under study, not proof of general legal reasoning.
4. RKM context contains additional semantic information and tokens. The experiment does not isolate formatting alone.
5. Underlying pretrained models may have encountered public OSHA text. Their pretraining contamination cannot be ruled out.
6. Only 24 scenarios, two models, and four related regulatory frameworks were evaluated; nominal annotation agreement is uneven.

A future confirmatory evaluation should independently author and freeze new scenarios before model runs, preserve training/development/test boundaries, adjudicate references separately from the unadjudicated IRR analysis, and test field ablations with matched context budgets.

## Human work remains

AI can retrieve, structure, export, propose and flag inconsistencies. People still verify source fidelity and version, exceptions and applicability, workplace facts, authentic evidence, ambiguity and final judgments. No hours-saved measurement or optimized human-review allocation was performed. Hashes fingerprint excerpts; they are not a temporal regulatory graph.
