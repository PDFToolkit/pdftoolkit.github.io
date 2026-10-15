# Protected native revisions

This guide covers the native protected-revision operations in core 0.10.0.

A valid signature protects its signed bytes. It does not, by itself, determine
whether later changes are permitted. The native writer verifies historical
signatures, classifies the entire emitted change and intersects every applicable
DocMDP, FieldMDP, Adobe field lock and authenticated usage-rights restriction.
The [certified-form tutorial](tutorials/37-protected-form-fill.md) shows one complete
operation with visible output.

## Keep the original native history

Use the `FileRevision` returned by native writing or verified signing in the same
runtime. Constructor-supplied snapshots, clones, PHP serialization and external
PDF bytes cannot recreate its emission authority. `PreparedSignature::finalize()`
can complete reserved bytes, but opaque bytes alone supply no verified historical
authority. Verified output binds the final bytes, signature dictionary, sole
Contents gap, ByteRange and actual signing credential.

All `IncrementalUpdate` entry points and direct `IncrementalWriter` calls use the
same guard. Removing `Perms`, replacing `Root`, detaching the AcroForm or renaming
a field cannot erase a historical restriction. The optional Reader can inspect
external PDFs; it does not turn them into authenticated native writer histories.

## Select a supported operation

These are the classifier's bounded operations, subject to all other historical
restrictions. A permission level is not general authority to edit the graph.

| Operation | Native protected scope |
| --- | --- |
| Fill an existing `Tx` field | P2/P3; direct plain text, fixed defaults/actions/flags, inherited ReadOnly and locks enforced, `MaxLen`/comb checked. |
| Fill an existing `Ch` field | P2/P3; fixed options, value and ordered `I`/`TI` consistent with the selected PDF version. |
| Change a checkbox/radio `Btn` | P2/P3; `V`, widget `AS` and existing Off/on appearances agree. Pushbuttons and replacing button appearance programs are excluded. |
| Replace a text/choice appearance | Preserve geometry, resource bindings and every byte outside an isolated variable-text region; see below. |
| Add/edit/detach markup | P3 only; the listed annotation subtypes and entries, with unchanged page ownership and surviving annotation order. |
| Add one native signature | Existing unsigned field, unchanged reservation or one new terminal signature field; the separate complete signing proof still applies. |
| Add DSS/document timestamp evidence | PDF 2.0 maintenance proof; additional Adobe P1 locks and usage rights are not relaxed. |
| Instantiate a page template | Not implemented by this native classifier. |
| Combine filling/annotation edits with signing or maintenance | Refused; classify them in separate permitted revisions. |

The markup allowlist is `Text`, `FreeText`, `Line`, `Square`, `Circle`, `Polygon`,
`PolyLine`, `Highlight`, `Underline`, `Squiggly`, `StrikeOut`, `Caret`, `Ink` and
`Stamp`. ReadOnly, Locked and LockedContents prevent editing. Widgets, new actions,
new relationships and unrelated dependencies cannot acquire annotation authority.
Detaching an annotation retains its historical object bytes.

Field identities, qualified names, parent/child structure, inherited flags/defaults
and widget ownership are checked against frozen revisions. Only the classified
value and selection changes are permitted. A terminal value cannot
bypass a read-only parent or a historical FieldMDP lock. Ambiguous names,
renaming, reparenting, extra aliases and unclassified objects are refused. New
appearance objects receive fresh identities; historical shared streams and
resource objects remain immutable. A fill never authorizes page-content changes.

## Preserve the variable-text boundary

For a non-rich text/choice appearance, ISO's replacement procedure uses one
`/Tx BMC`…matching `EMC` region; when absent, append a new region. The native
classifier preserves every decoded prefix/suffix byte and the old geometry.
Instructions inside the region must own their `q`/`Q` isolation. Marked content
alone does not save graphics state; paths, pending clipping and text objects
cannot cross the region or graphics-restoration boundaries.

The bounded lexer recognizes comments, escaped names/strings and containers,
so a fake `EMC` in a string cannot widen the replaceable region. It supports plain
bytes or one `FlateDecode` without predictors. Defaults are 1 MiB encoded and
decoded bytes, 100,000 tokens and nesting 64. Multiple/nested Tx regions, inline
images, unknown operators and Type3 glyph operators are refused. Existing resource
names retain their bindings; added names can refer only to unchanged historical
objects. Existing appearance alternatives and state names are retained; adding
R/D alternatives or states without a comparable historical program is refused.
This is a region/state proof, not a complete graphics-language validator
or proof that rendered glyphs match the field value. Rich text and arbitrary
appearance regeneration remain outside scope.

## Authorize UR3 explicitly for each update

Clear native UR3 history with transform `V=2.2` requires an application-selected
`UsageRightsAuthorization`. The `UsageRightsAuthority::permits()` callback receives
the actual `VerifiedRevisionSignature`; its `facts` expose verified algorithms
and the bound signing certificate. The application decides whether that identity
may grant usage rights. Mathematical validity, a self-declared PDF policy or a
certificate's mere presence does not establish that authority or PKI trust.

```php
use PDF\Document\Signatures\UsageRightsAuthorization;
use PDF\Document\Signatures\Policies\UsageRight;
use PDF\Syntax\FileStructure\IncrementalUpdate;

$authorization = new UsageRightsAuthorization($authority, UsageRight::FillField);
$update = new IncrementalUpdate($nativeRevision, $replacementBody, null, null, $authorization);
$next = $update->toRevision();
```

`$authority` is an explicit application implementation of `UsageRightsAuthority`;
`$nativeRevision` and `$replacementBody` are the actual native history and staged
objects. The nonempty operation scope applies to this update only. Every actual
fill, annotation create/modify/delete or signing operation must belong to both
the signed rights and that scope, and respect DocMDP/FieldMDP/Adobe restrictions.

Saving is evaluated separately per operation. In ISO 1.7, nonrestrictive `FillIn`
needs signed `FullSave`; an unrelated annotation right cannot supply saving for
it. Restrictive rights, annotation modification and actual signing retain their
specified saving rules. Application scope `FillField` authorizes a persisted
fill when the signed policy permits saving; it does not additionally require
application `FullSave` solely because signed `FullSave` supplies that condition.

PDF 2.0 accepts only explicit restrictive `P=true` here. Its different
`P=false`/absent semantics are not interpreted as ISO 1.7 rules. Legacy `UR`,
encrypted UR history, unverified/opaque signatures, denied authority and
unclassified maintenance/general-save operations remain refused. UR is deprecated
in PDF 2.0; PKI chain and revocation policy remain application responsibilities.

## Read the evidence and its limits

The independent validation matrix runs unchanged pyHanko 0.37.0, qpdf and Poppler
on PHP 8.3/8.4/8.5. Per runtime it records 97 native refusals, 148 checked PDFs,
32 native form combinations and 32 independent fills, four P3 annotation chains
and 198 pixel checks. UR3 adds eight signed sources, three permitted fills and
11 independently verified CMS files, with signed-byte tampering detected.
Those counts describe CMS, structure and rendering evidence, not 148 approvals
of modification policy or an independent granting-authority decision.

| Independent observation | Interpretation |
| --- | --- |
| pyHanko confirms 16 `Tx`/`Ch` combinations | Those value-change cases agree with its unchanged modification policy. |
| All 32 filled button outputs and 12 P3 annotation operations report `OTHER` and `docmdp_ok=false` | Values, appearance states, CMS and rendered pixels are checked separately; the oracle's policy is not patched. |
| Two ReadOnly changes pass pyHanko | The native classifier refuses them; ReadOnly and FieldMDP are distinct controls. |
| Tutorial 37 reports `OTHER` | Its changed AP belongs to a widget child without `/T`; CMS/ByteRange and rendering checks do not imply pyHanko DocMDP approval. |
| Strict pyHanko rejects hybrid signature validation | Its matrix uses Table/Stream; native hybrid tests are separate. |

The sources are ISO 32000-1:2008, physical pages 440–444, 478–482 and 485;
ISO 32000-2:2020 EC3, physical pages 545–549, 560, 588–592, 606 and 607–608;
and the Adobe supplement, physical page 43. The core's retained
`resources/signature-revisions/coverage.json` records their exact SHA-256 hashes.
Templates, general field creation/deletion, new resource objects, external-chain
classification, complete graphics validation and human appearance/intent review
remain explicit boundaries.

[Certified-form tutorial](tutorials/37-protected-form-fill.md) · [Security](security.md) · [Incremental revisions](tutorials/11-incremental-update.md)
