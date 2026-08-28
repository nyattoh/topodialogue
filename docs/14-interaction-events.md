# Observable interaction-event protocol

This protocol extends the Phase-1 transcript trajectory without treating an
unobserved mental state as data. It is an instrumentation protocol, not a
clinical or psychological coding scheme.

## Unit and labels

The unit is one normalised dialogue turn. An annotator may assign zero or more
labels. Every assignment must identify an observable span or turn relation.

| Label | Include when | Exclude when |
|---|---|---|
| `revisit` | the turn visibly returns to wording or a coded semantic region used earlier | merely shares common function words |
| `repair` | the speaker explicitly corrects or reformulates an earlier expression | ordinary elaboration without correction |
| `rejection` | a proposal, characterisation, or frame is explicitly declined | grammatical negation inside an explanation |
| `adoption` | a proposal or frame is explicitly accepted for use | politeness or acknowledgement alone |
| `handover` | a question or explicit invitation offers the next move to the other speaker | rhetorical questions without a speaker change |
| `reframing` | the turn explicitly substitutes an assumption, viewpoint, or abstraction | a new topic with no relation to the prior frame |
| `pause` | the log contains an explicit pause, silence, or interruption marker | ellipses, fillers, or delayed timestamps without an agreed threshold |

The deterministic extractor produces **candidates**, never gold labels. Its
marker list and recurrence threshold are versioned. Japanese explanatory
`ではなく` is not itself treated as rejection. A question plus speaker change
is a structural handover candidate; it is not a claim about intention.

## Transportability and calibration

The current marker pack is Japanese-specific. Do not reuse it unchanged for a
different language, community, relationship, or task. A new setting requires:

1. a versioned marker pack and exclusion list;
2. independent annotation on examples from that setting;
3. threshold selection without using the final evaluation conversations; and
4. comparison against individual, relationship, and context baselines.

These baselines describe observed interaction histories. They must not be
converted into demographic stereotypes or a fixed personality profile. An
event count never establishes nationality, culture, intention, or an unspoken
mental state.

## Independent annotation and agreement gate

Two annotators receive the same turn identifiers and work independently. The
annotation file is:

```json
{
  "case_id": "real-case-01",
  "annotator_id": "anon-a",
  "turns": [
    {"turn_id": "t1", "labels": ["handover"]},
    {"turn_id": "t2", "labels": []}
  ]
}
```

Run `python -m topodialogue.cli agreement a.json b.json -o agreement.json`.
The report gives per-label observed agreement, Cohen's kappa, and positive-class
F1. A label absent from both files has undefined kappa and F1 (`null`), not a
perfect score. Disagreements are adjudicated only after the independent report
has been frozen. Until this gate is run with real annotators, automatic counts
must be described as surface-marker candidates.

## Public derivative

`prepare-case` writes a derivative that withholds every utterance. It retains
speaker order, coarse length/form metadata, pseudonymous recurrence regions,
and event candidates. Only recurrence regions and event types enter trajectory
features; common length and question/statement bins do not, because they can
manufacture false revisits. Automatic pattern scanning cannot prove anonymity,
so the raw transcript remains local and is never included in the release bundle.
