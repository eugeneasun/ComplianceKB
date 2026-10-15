# Reproducibility

## Offline reproduction: no credentials or model downloads

From this repository's root, with Python 3.12 or later:

```bash
python tools/check_release.py
python tools/demo.py --query "employee training records"
python tools/reproduce.py
```

The last command validates datasets and saved-call completeness, recomputes the model summaries and paired bootstrap intervals into `generated/llm_analysis/`, checks numerical agreement with the reported summaries, recomputes retrieval scores from stored rankings, and recomputes annotation agreement from anonymized paired labels. It does not call an API. Saved model outputs have provider service envelopes removed, but retain every parsed answer and field used by the scorer.

For full JSON Schema validation rather than built-in structural checks:

```bash
python -m pip install -r requirements-dev.txt
python tools/reproduce.py
```

## Retrieval reruns: optional dependencies and downloads

Install `requirements-retrieval.txt` in a separate environment. The recorded experiment used Python 3.12.14, sentence-transformers 6.1.0 and PyTorch 2.14.0+cpu. The E5 sensitivity manifest records additional library versions. These are recorded historical configurations, not a guarantee that every pinned package is available on every platform. Model availability and future package resolution are outside the offline reproducibility claim.

See the command-line help for the explicit retrieval parameters:

```bash
python research/benchmark/run_retrieval_benchmark.py --help
python research/benchmark/dense_baseline.py --help
python research/benchmark/hybrid_baseline.py --help
```

Use a new output directory; preserve frozen rankings and results. Dense tests may explicitly skip when dependencies/model weights are missing; a skipped test is not an executed dense rerun. The historical MiniLM manifest does not pin a model revision, so exact historical embedding reconstruction cannot be guaranteed. E5 has a pinned revision in its manifest.

## Paid model reruns: opt-in only

The saved model IDs are `gpt-5.6-terra` and `claude-sonnet-5`, reasoning effort `low`, a 2,000-token output cap, and no explicitly comparable temperature setting. Those are the recorded IDs, not a promise that a provider currently exposes them.

The runner reads `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` from the process environment. Supply your own credentials privately; never place values in tracked files. No credentials are included in this repository.

To inspect options without a paid request:

```bash
python research/benchmark/run_llm_benchmark.py --help
```

If deliberately rerunning, choose a fresh `--output-dir` and your own `--budget-per-provider`. Historical pricing estimates are not current provider prices; the runner's budget guard is an estimate, not a provider-side hard spending cap. Do not rerun into the frozen experiment directory. Exact output equality is not promised for a live model rerun.

## Integrity and sanitization

`RELEASE_MANIFEST.sha256` covers the curated release contents. Dataset and scenario bytes are unchanged. Path-bearing run manifests are sanitized to relative paths. Provider `raw_response` envelopes are omitted to avoid publishing service identifiers; all scoring data remains. The public annotation file is a projection of unchanged labels, not a new annotation exercise. See `research/annotation/README.md`.
