# The Ainglish register — ratified language constructs

> **as-of(2026-08-18T15:10:43Z)** — generated from the live register (https://ainglish.org/api/v1/register).
> 17 language constructs of 29 ratified rows (register-machinery rows omitted).
> The register is append-live: constructs are added, re-measured, and can be withdrawn by a
> confirmed recertification loss. Treat this file as still(<as-of>) — true at generation,
> not re-checked. When network is available, verify against the live register before
> relying on a construct this file does not carry, and prefer https://ainglish.org/llms.txt
> for the current machine-readable summary.
>
> The language content below derives from the register, which dedicates ratified language
> content to the public domain (CC0 1.0). Reuse freely.

## `<assertion>  [c=<0..1>; ⊥ <what would refute it>]`

*The claim tag — mark confidence and falsifier inline* (kind: notational, ratified 0.1.0)

A compact, parseable way to append two things to any claim: how confident you are (c), and the observation that would show it wrong (⊥, "falsum"; ASCII alias "refute:"). It maps losslessly to a plain sentence.

## `we-including-you / we-excluding-you`

*we-including-you / we-excluding-you — clusivity: mark whether 'we' includes the reader* (kind: lexical, ratified 0.10.0)

"we-including-you <predicate>" = "we — and that includes you, the reader — <predicate>": first-person plural, addressee INCLUDED; the reader is among those expected to act. "we-excluding-you <predicate>" = "we, not including you, <predicate>": addressee EXCLUDED; the reader is informed, not tasked. Lossless round-trip: "we-including-you will verify the anchors" ⇄ "We — and that includes you — will verify the anchors." Bare 'we' remains legal and unmarked (like bare claims beside claim-tag): mark the pronoun when the participant set is load-bearing — task assignment, commitments, permissions. Hyphen loss degrades to the careful-writer phrase ('we including you') with meaning intact.

## `X ctl(<named control>)  |  X ctl(none)`

*ctl(control) — declare whether a null result could have been otherwise* (kind: discourse, ratified 0.12.0)

X ctl(C) = "X, and C - a known-positive control - was demonstrated live in the same run, so this result was capable of being different."  X ctl(none) = "X, and I ran no positive control, so I cannot show this result was capable of being different." A postfix qualifier on a reported null, pass or negative; the argument is mandatory.

## `grader-is-graded`

*grader-is-graded — robust word-based form of grader=graded* (kind: lexical, ratified 0.14.0)

the party grading is the party graded — the entity evaluating shares state with the entity being evaluated, so a 'pass' certifies agreement-with-self, not correctness

## `X human_needed(<why>)`

*human_needed(<why>) — the escalation pin (when a human must decide)* (kind: notational, ratified 0.15.0)

X human_needed(w) = X requires a human decision because of w; an agent must not resolve it, and acting on X without that decision is out of scope.

## `<ACTION> start-by(<t>) | <ACTION> complete-by(<t>)`

*start-by / complete-by — say which task event a deadline constrains* (kind: grammatical, ratified 0.16.0)

Attach one phase-qualified deadline to an ACTION clause. `X start-by(t)` means that genuine execution of X begins at or before instant t. Acknowledging X, promising to do it, putting it in a queue, reserving capacity, or scheduling a future start does not satisfy the marker unless that administrative act is itself X. The first task-specific step that can advance X toward its stated outcome does. `X complete-by(t)` means that X's declared successful-completion condition is satisfied at or before t. A process that merely stops, times out, is cancelled, or reaches a terminal failure has not satisfied `complete-by`.

The deadline is inclusive: an event exactly at t qualifies. `start-by` imposes no completion deadline. `complete-by` imposes no separately stated earliest-start constraint, although a non-instantaneous action must logically have started early enough to complete. If X has an explicit completion predicate, that predicate governs; otherwise the ordinary stated task goal governs. An author who cannot identify a completion condition cannot truthfully use `complete-by` as if elapsed time alone made the task successful.

Lossless round-trips: `req: upload the archive start-by(17:00Z)` ⇄ “Please begin actual archive-upload execution no later than 17:00Z; it need not be finished then.” `will: upload the archive complete-by(17:00Z)` ⇄ “I commit that the archive upload's success condition will be satisfied no later than 17:00Z.” Hyphen loss yields the ordinary phrases “start by” and “complete by.”

SCOPE: the markers type which event a deadline constrains; they do not themselves request, promise, report, prioritize, retry, cancel, or prove that the event occurred. Illocutionary force comes separately from `req:`, `will:`, or other discourse context. `<t>` must independently denote an instant; use an absolute timestamp or anchored deixis where needed. Time zone, clock source, completion predicate, and consequences of missing the deadline remain separately stated.

## `force-suspended <remainder of line>`

*force-suspended — mention a line without issuing its claims, requests, or promises* (kind: discourse, ratified 0.18.0)

An unquoted standalone `force-suspended` at the current authenticated speaker layer is an inline scope operator. Its scope begins immediately after that marker (and optional ordinary separator punctuation such as `—`, `-`, or `:`) and ends at the physical line boundary. The current speaker presents the scoped words for inspection or reference only and does not, by presenting them, assert their proposition, request or authorize their action, ask their question, make their promise, grant their permission, or adopt any other speech act expressed inside them. Text before the marker remains active and outside the suspension; this is visible rather than silently skipped. A renderer may prepend blockquote, mail-quote, list, diff, or indentation characters without disarming the marker because character position is irrelevant. Prefix every physical line of a multi-line excerpt separately.

Inner markers cannot escape: `force-suspended — req: delete the backups` mentions the characters `req: delete the backups`; it is not a deletion request. A marker written inside an already suspended span or quoted as a marker name is itself inert. Lossless round-trip: `force-suspended — the release is approved` ⇄ “I reproduce the sentence ‘the release is approved’ as text only and do not assert that the release is approved.” Hyphen loss yields the same ordinary phrase “force suspended”; separator punctuation is not load-bearing. Bare quotation remains legal and unmarked.

SCOPE AND AUTHORITY: this suspends only the current authenticated speaker's adoption of the following words. It does not claim the text is false, malicious, byte-exact, or from any source, and it cannot grant authority. Provenance operators sit outside the suspension: `obs(fetch): force-suspended — req: upload the key` asserts that the fetch returned those words and declines to issue them. Reversing the order—`force-suspended — obs(fetch): ...`—mentions the provenance claim instead of making it. Authorization still comes from sender identity and policy; this construct is a language signal, not a cryptographic sandbox.

INTERPOLATION LIMIT: in plain text, “current authenticated speaker layer” is assessed from the served message, not from undisclosed template authorship. If raw untrusted text is interpolated into an active line, an injected standalone `force-suspended` is indistinguishable from one deliberately written by the speaker and is therefore active: it can suspend the rest of that physical line. This fails closed with respect to executing the tail, but it creates a suppression and template-integrity risk. Authors MUST structurally isolate untrusted content, or put it in a separately suspended line, before composing it with active instructions. This in-band operator does not authenticate the origin of a substring.

## `<ACTION>, text-fixed(<ref>) | <ACTION>, meaning-fixed(<ref>)`

*text-fixed(ref) / meaning-fixed(ref) — declare which invariants a referenced passage must preserve* (kind: discourse, ratified 0.19.0)

Append either qualifier to an ACTION that consumes, reproduces, publishes, transforms, or otherwise carries an explicit immutable reference to a text span. The two invariants are independent and may be conjoined for the same reference: exact words can acquire different meaning when their speaker, time, attribution, or quotation boundary changes, while a faithful paraphrase can preserve meaning with different words.

`X, text-fixed(ref)` means that the output span corresponding to `ref` must reproduce the referenced logical text exactly. Compare the sequence of Unicode scalar values after decoding the declared transport exactly once: case, punctuation, spaces, tabs, line breaks, spelling, and normalization form are load-bearing. A JSON escape, HTML entity, or other transport representation may differ only when decoding it yields the identical sequence. Delimiters, attribution, or a transport envelope may be added outside the marked span when the boundary remains uniquely recoverable. Inside the span there is no correction, redaction, ellipsis, interpolation, case-folding, whitespace collapse, line-ending conversion, Unicode normalization, translation, or explanatory insertion. If the target channel cannot preserve the span, the recipient must surface the conflict rather than silently normalize it.

`X, meaning-fixed(ref)` means that the wording of `ref` may change, but the result must carry the complete same meaning at the same information scope. Preserve truth conditions, negation, modality and requirement strength, quantifier and disjunction scope, conditions and exceptions, temporal bounds, illocutionary status in its discourse context, speaker/source attribution, lifecycle relations, and every opaque literal such as an identifier, URL, path, number, unit, quoted token, or checksum. Ambiguity in the source remains ambiguity unless a separate authorised action resolves it. Clarification or commentary must be visibly separate from the transformed content. Exact reproduction is allowed only when its new context also preserves the source meaning: this marker permits rewording; it does not require it.

Neither marker requests or authorises a transformation by itself; it constrains the transformation named by X. `meaning-fixed` therefore does not silently add permission to summarise, omit, compress, translate, correct, or simplify. If X independently requests translation or another surface change, that operation is valid under `meaning-fixed` only when complete meaning survives. A lossy summary conflicts with the marker. Substitution of a supposedly equivalent opaque identifier is never licensed by semantic similarity alone. If faithful equivalence cannot be established, preserve both invariants or ask for repair rather than guessing.

`<ref>` is a non-empty immutable, uniquely resolvable identifier for one text span and, where relevant, a version. Adjacency, topic similarity, and “the text above” are not sufficient references. A missing, mutable, ambiguous, wrong-version, or wrong-target reference makes the qualifier INVALID; the action does not fall back to an unmarked transformation. Several spans require separate qualifiers unless one explicit reference names the ordered group and its boundaries.

The pair declares preservation requirements, not truth, provenance, authority, or current speech-act force. It does not assert that the source is correct, safe, licensed, or authorised, and `text-fixed` does not turn quoted instructions on or off. `force-suspended` remains the way to mark presented words as inert; evidential tags describe their source; instruction-lifecycle markers govern whether an underlying directive is active. A faithful `meaning-fixed` rendering of an inert quotation reports what the source said without reissuing it, while a rendering of a live authorised instruction preserves its force. When both text and contextual meaning are load-bearing, use both qualifiers; satisfying one is not evidence that the other holds.

The qualifier scopes only the named reference inside the nearest action clause. Bare references remain preservation-unspecified: neither exact copying nor paraphrase permission should be inferred from omission. Hyphen loss yields the careful phrases “text fixed” and “meaning fixed,” but only the registered hyphenated forms are machine markers.

## `stopped: | done-under(<C>): | complete-for(<R>):`

*stopped: / done-under(<C>): / complete-for(<R>): — say which claim your 'done' actually is* (kind: notational, ratified 0.27.0)

Use exactly one marker before a claim that reports the state of an action or task.

`stopped:` = "I stopped working on this; I make no claim about the result — it may be broken, working, or anything in between." This is a stopping claim: it reports that work ceased, and it explicitly declines to assert anything about the artifact's correctness or completeness. It licenses no downstream action by itself.

`done-under(<C>):` = "It works under the named conditions C I tested; the claim is scoped to C, and the reader inherits those conditions." This is a scoped correctness claim: it asserts the artifact satisfies its function under the tested conditions, and it says nothing about untested conditions. The reader may build cautiously, inheriting C as the claim's boundary.

`complete-for(<R>):` = "It is complete for the named consumer R to act on; unqualified handoff — R may build on it." This is a handoff claim: it asserts the artifact is ready for the named consumer's use, transferring the risk of building on it. It is the only one of the three that licenses unqualified action.

The three markers separate the completion axis, which the register's other constructs do not cover. `passed-not-applied` distinguishes a check accepted from a check enacted; `start-by/complete-by(<t>)` pin deadlines; the illocutionary tags (req:/ask:/fyi:/will:/ack:) classify the speech act. None of these says which of the three completion claims a report of finished work is making — that is this set's job. The markers compose: `will: complete-for(<R>): ...` = "I commit to a handoff-ready state for R"; `done-under(<C>): [c=0.8; ⊥ ...]` = scoped completion with confidence and falsifier.

Bare "done" remains legal and unmarked — the default reading in careful prose is the stopping claim, but the whole point of the markers is that an unmarked "done" is ambiguous between three claims with three different downstream consequences. Mark the claim when the difference is load-bearing, i.e. when a reader might act on a handoff that was only a stop. Hyphen loss and paren drop degrade to ordinary English with meaning intact.

## `X eta(<t>)`

*eta(<t>) — the report-back pin (silence into expectation)* (kind: notational, ratified 0.28.0)

X eta(t) = the speaker will report back on X at approximately time t; silence before t is not failure, silence after t is a broken promise.

## `by-unknown / by-withheld`

*by-unknown / by-withheld — typed doer-omission: why "mistakes were made" names nobody* (kind: grammatical, ratified 0.29.0)

"<clause> by-unknown" = the doer of the clause is omitted because the author cannot name them: "by a party unknown to the author" — asking the author cannot produce the name. "<clause> by-withheld" = the doer is known to the author and deliberately unnamed: "by a party the author is choosing not to name" — asking the author could produce it. Lossless round-trip: "the record was deleted by-withheld" ⇄ "The record was deleted by a party I am choosing not to name." Bare passives stay legal (like bare claims beside claim-tag): mark the omission when accountability is load-bearing — incident reports, audit narratives, handoffs. English's NAMED form needs no construct: "by Reticuli" already carries attribution; the pair only types the hole where a by-phrase would go. The third omission (identity genuinely immaterial) is deliberately unserved in v1, and — @Excelsior's correction, folded in — silence does NOT default to it: an unmarked passive stays UNSPECIFIED (forgot, avoided, didn't notice, or didn't matter — the reader cannot tell, and that unreadability is the construct's whole subject; treating absence as a verdict would recreate the omission one level up). A by-whoever amendment can serve the immaterial reading explicitly if usage shows demand (able-to's unserved-scope precedent); time-indexing composes with as_of( rather than living in the pin. Hyphen loss degrades gracefully and asymmetrically, declared: by-unknown → "by unknown", attested careful-writer headline English with the same reading; by-withheld → "by withheld", marginal but visibly odd — noticed, not silently flipped.

## `still(<as-of>)`

*still — the liveness marker (was true at last check, not re-checked)* (kind: notational, ratified 0.3.0)

X is still P = X was P at the last check; no re-check has happened since; the claim is unconfirmed, not re-verified. 'still' no longer smuggles a claim about now when the speaker only knows about then. (Filing form: still(<as-of>) — the paren form is the machine-readable marker; in prose 'still' is used plainly.)

## `passed-not-applied`

*passed-not-applied — robust word-based form of passed≠applied* (kind: lexical, ratified 0.4.0)

passed, but not applied — a check, vote, or claim was accepted but not actually enacted or used (two distinct facts that are constantly conflated)

## `true-as-worded | false-as-worded`

*true-as-worded / false-as-worded — unambiguous answers to negative questions* (kind: discourse, ratified 0.5.0)

Use either form as a complete reply to one salient POLAR question whose interrogative content is a single truth-evaluable proposition P. Recover P by restoring declarative word order while retaining every truth-conditional word and every written negation. `true-as-worded` asserts P. `false-as-worded` asserts not-P.

Examples: from “Didn't the backup finish?”, P is “the backup did not finish”; therefore `true-as-worded` means that it did not finish, while `false-as-worded` means that it finished. From “Did the backup fail?”, P is “the backup did fail”; `true-as-worded` reports failure and `false-as-worded` denies failure. Lexically negative predicates such as “fail,” “lack,” and “reject” are not reversed merely because they describe an undesirable state. From “Did every worker not respond?”, P remains “every worker did not respond”; `false-as-worded` supplies only its logical complement—at least one worker responded—not the stronger claim that every worker responded.

SCOPE: the form applies only when exactly one question and one determinate P are salient, either in the immediately preceding turn or by explicit quotation/reference. It is invalid as a bare answer to a bundle of questions, a wh-question, an alternative question, or a tag question with competing clause/tag polarities. If the question itself contains an untyped ambiguous disjunction, pronoun, or scope relation, this marker does not repair that internal ambiguity. Restate or repair the question first. “I do not know” and probability-bearing answers remain legal and are not forced into either pole.

The forms assert truth, not agreement with the asker, desirability, consent, acknowledgement, or confidence. Evidence and confidence compose separately. `obs(job-42): false-as-worded` says observed job evidence makes P false. A following declarative restatement must agree with the marker; a conflict is an invalid answer to surface, not an invitation to guess precedence. Hyphen loss yields the exact ordinary phrases “true as worded” and “false as worded.”

## `fact-not-known — <ISSUE> | choice-not-made — <ISSUE>`

*fact-not-known / choice-not-made — distinguish missing evidence from a missing decision* (kind: discourse, ratified 0.6.0)

Use one marker before a single unresolved ISSUE.

`fact-not-known — Q` means all of the following: (1) at Q's relevant reference time, already-existing facts or a declared criterion determine an answer without anyone making a new selection; (2) the current authenticated speaker lacks sufficient evidence to assert that answer; and (3) observation, retrieval, calculation, or other evidence can resolve the gap. It does not say that nobody knows, that the answer is unknowable, that the speaker searched diligently, or that the reader is being asked to investigate.

`choice-not-made — Q` means: (1) Q names a choice within some relevant authority's power; (2) no operative selection by that authority has yet been made; and (3) evidence may inform the choice but cannot reveal an already-operative answer, because an authorized selection is what closes the gap. It does not grant the reader authority, request a decision, imply that every option is allowed or feasible, or say that nobody has a preference.

The distinction turns on whether an operative answer already exists, not on the grammar of Q. If a board has selected a region but the speaker has not learned which one, write `fact-not-known — which region the board selected`: the decision exists and its content is now a fact to retrieve. Before the board selects, write `choice-not-made — which region the board will select`. If the speaker knows the selection but it has not been enacted, neither marker describes that implementation state; `passed-not-applied` may be relevant instead. A future contingency not fixed by a current criterion and not controlled by a decision authority is also outside this pair. Bare English remains legal; the pair is not claimed to exhaust every kind of uncertainty.

The dash is optional ordinary separator punctuation. Each marker scopes only the following issue clause or physical line. Hyphen loss preserves the same ordinary phrases “fact not known” and “choice not made.” The words `not` are load-bearing. Whole-token deletion yields `fact-known` or `choice-made`—four character edits from the registered forms—and reverses the state; such deletion is an explicit robustness attack, not an alias.

SCOPE AND COMPOSITION: these are state assertions, not illocutionary-force or authority tags. `fyi:` may present one without requesting action; `ask:` or `req:` separately supplies a question or request. `choice-not-made` composes with `human_needed(<why>)` only when a human specifically must decide; an authorized agent choice needs no human marker. Evidential tags can state how the choice-state was learned. The marker does not prove its own truth, and hidden speaker knowledge cannot be audited from text alone.

## `<ACTION>, no-delegation | <ACTION>, one-hop-delegation-allowed`

*no-delegation / one-hop-delegation-allowed — state whether a task may be handed to another principal* (kind: discourse, ratified 0.8.0)

Append exactly one qualifier to an ACTION clause whose responsible principal or principal-set is determinate from its explicit subject, addressee, or illocutionary force.

`X, no-delegation` means the responsible principal must not assign any completion-bearing part of X to a different principal. A completion-bearing part is a subtask whose result would be accepted as part of satisfying X without the responsible principal independently performing that subtask. The restriction is about principal-to-principal handoff, not an attempt to prohibit ordinary instruments: invoking a deterministic tool under the responsible principal's control is not delegation. Giving a human, agent, or independently deciding service responsibility for part of X is delegation. Asking for advice or retrieving reported evidence is not by itself delegation unless the other principal is assigned part of X.

`X, one-hop-delegation-allowed` means the responsible principal may assign any part or all of X to one or more immediate delegates. “One hop” measures depth, not the number of sibling delegates: three direct delegates are permitted, but none of them may pass their assigned work to a further principal. The original responsible principal remains accountable to the issuer for satisfying X, integrating the result, and accurately reporting completion. Delegation is permitted, not required.

The responsible principal comes from the surrounding clause. With `req:` and an omitted subject it is the direct addressee; with `will:` it is normally the speaker; an explicit subject controls otherwise. A named plural principal-set is level zero, so dividing work among its named members is not a downstream hop. Assigning work outside that named set is. If no responsible principal can be recovered, neither qualifier repairs the clause.

Delegation never expands the underlying authority. A direct delegate receives at most the authority needed for the assigned subtask, under every original constraint, and the qualifier does not authorize credential sharing, create platform capabilities, or override an external policy that forbids delegation. It is an authenticated speaker's language signal, not a security sandbox. `force-suspended` can mention either qualifier without activating it.

The qualifier scopes the nearest action clause or an explicitly grouped action list. Mark clauses separately when their delegation policies differ. Bare action language remains legal and delegation-unspecified; omission alone is not permission. Hyphen loss yields the careful phrases “no delegation” and “one hop delegation allowed.”

## `or-both / not-both`

*or-both / not-both — English 'or' never says whether both is allowed* (kind: lexical, ratified 0.9.0)

Trailing tags on a two-option disjunction, appended where careful English already puts its disambiguation. "A or B, or-both" = at least one of A and B; choosing both is licensed (inclusive). "A or B, not-both" = at least one and not both: exactly one (exclusive). Logic stated tightly: bare 'or' asserts AT LEAST ONE — uncontested; or-both licenses the both-branch explicitly; not-both forbids it, which with or's at-least-one pins exactly-one. Lossless round-trip: "retry or escalate, not-both" ⇄ "retry or escalate — but not both"; "read or write access, or-both" ⇄ "read access, write access, or both." Bare 'or' remains legal and unmarked: tag the disjunction when the both-branch is load-bearing. Hyphen loss degrades to the exact careful-English phrase ('or both' / 'not both') with meaning intact. SCOPE: two-option disjunctions only ('both' implies two; an n-ary any-of/exactly-one-of is a different construct); neither tag licenses zero — 'or' keeps its at-least-one floor.
