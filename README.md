# india-hr-bench

How well do LLMs handle **Indian HR and hiring** work? Code-verified, source-cited, versioned.

> v0.1 — seed set only. Results table is empty until models are run. Do not cite numbers that are not here.

## Why this exists
Most LLMs were trained before India's four Labour Codes took effect (21 Nov 2025). They also miss
Indian hiring realities: notice-period buyouts, CTC vs in-hand, Hinglish candidate messages.
This benchmark measures where models fail, and whether they ask instead of guessing.

## Tracks
| Track | Tests |
|---|---|
| `labour_codes` | Wage definition / 50% rule, gratuity, effective dates (staleness trap) |
| `ctc_math` | Code-generated salary and gratuity arithmetic |
| `hiring_ops` | Notice period, joining dates; should-ask-first behaviour |
| `hinglish` | Extraction from Hinglish candidate messages |
| `screening_bias` | Ranking on job-relevant criteria only |

## Item schema (`data/*.jsonl`)
`id, track, answer_type (exact|numeric|extract|clarify|behavior), prompt, expected, source, trap, as_of, review_status`

Every legal-rule item carries `source` and `as_of`. Items stay `needs_review` until checked against
official text by a practitioner. Not legal advice.

## Metrics
accuracy per track · **staleness rate** (answers using pre-Codes rules) · **ask-rate** on under-specified items ·
robustness gap (original vs reworded vs distractor).

## Run
```
python generators/gen_numeric.py 20 > data/numeric_v0.jsonl
```
Reuse the runner from `reasoning-bench`.

## Contribute
Found a wrong ground truth? Open an issue with the official source link.
