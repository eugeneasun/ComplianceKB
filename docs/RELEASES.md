# Release notes

| Release | Records | Change | Reported model evaluation |
|---|---:|---|---|
| v1.2.0 | 108 | Corrected and author-reviewed experimental corpus | Yes: 24 scenarios / 240 responses |
| v1.3.0 | 113 | +5 coverage-audit requirements | No |
| v1.4.0 | 131 | +18 coverage-audit requirements | No |
| v1.5.0 | 133 | +2 HazCom requirements requiring manually supplied verbatim source text | No |

v1.3.0 adds anti-retaliation and separate documentation/certification requirements. v1.4.0 adds further candidates from the four-framework coverage audit. v1.5.0 adds HazCom SDS shipment timing and small-container labeling records. Each release preserves the earlier record set and adds records; the public checks verify this property.

All four releases are copied unchanged from the research workspace, including the source hashes and export manifests. Later coverage additions do not imply exhaustive legal coverage or the same validation strength as the evaluated experimental corpus.

Historical v1.0.0 data, simulated IRR demonstrations, incomplete review templates and draft scenario generation artifacts are excluded to avoid confusing them with the corrected experiment. The legacy `retrieval_provisional` directory name is retained because the saved development analysis references its rankings. Its manifest correctly records its earlier scenario-file hash; it must not be relabeled as an independently confirmed test run.
