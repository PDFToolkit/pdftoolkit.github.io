# Using core 0.5

Core 0.5 retains PHP 8.3 as its minimum, with CI on PHP 8.3, 8.4 and 8.5.
Since version 0.1.3, modules accept core series 0.2, 0.3, 0.4 and 0.5; they
remain optional for an application that only generates PDFs.

```bash
composer require 'roukmoute/pdf:^0.5'
```

Install the core and chosen modules from Packagist as explained in the
[package guide](packages.md). To develop in the core checkout, set
`COMPOSER_ROOT_VERSION=0.5.x-dev` before `composer install`.

## Revisions and identifiers

`FileRevision::previous` retains the previous revision. Snapshots expose
actually emitted dictionaries and remapped references. Streams have a
`RevisionStreamSnapshot` containing their encoded bytes before encryption.
This evidence does not serialize as a new stream; explicitly construct
a new object to supply new data and its filters.

`LinearizedWriter::revision()` now returns a revision usable by
`IncrementalWriter`. Appending a revision preserves the exact prefix and
makes the resulting file non-linearized, following Annex F.

`ReleaseIndirectObject` and `ReuseObjectNumber` describe free-list operations.
A removed alias retains its original identifier to write a stale reference;
`binding()` remains reserved for live objects. A reused value receives its
new generation and does not inherit the removed value's aliases. See the
[generation tutorial](tutorials/25-object-lifecycle.md).

## Navigation and embedded files

The `PDF\Document\Navigation` namespace provides labels, destinations,
articles, beads, transitions and presentation sequences. Checks concern
the actually written catalog and pages, including after incremental
replacement. An old object that becomes unreachable can remain in history.

The `PDF\Document\Files` and `PDF\Document\Collections` namespaces construct
specifications, embedded streams, their relationships and collection
metadata. Naming keys are PDF bytes, distinct from local paths. Content
is explicitly supplied; no external path is loaded.

Generated definitions correct two source interpretations: `CIEntry` now
requires an `IndirectReference`, and the historical `F` entry no longer
requires PDF 1.7. `UF` and collections retain their PDF 1.7 threshold.
Printed wording and the correction's justification remain accessible.

## Signing a field with its policies

`SignatureFieldSigning` composes a field, its reservation and its policy
contract. `bindCatalog()` explicitly binds document references.
`PreparedSignature::signWithPolicy()` and `finalizeWithPolicy()` provide the
same contract for an external backend or an already-produced result. The
verifier must cryptographically verify the result over the exact reserved
bytes before `Contents` is filled.

Seeds, lock, certificate, appearances and catalog data come from the written
snapshot. Advertising timestamp or revocation capability does not replace
verified evidence in the produced signature. The native OpenSSL backend
also verifies results from the simple signing API.

Digest negotiation reflects the actual backend: PHP currently emits CMS
with SHA256, while the native PKCS#1 format uses RSA/SHA1. An external
backend can offer other choices with its verifier. Table 234's DSA/SHA1
interpretation applies to the `DigestMethod` seed; a seed containing only
reasons does not restrict table 257's general possibilities.

Historical intrinsic checks prevent a false first certification, an Adobe
permission elevation or signing a locked field. General comparison of
changes permitted by DocMDP, FieldMDP and UR remains separate and must not
be inferred from these checks alone. See the
[field-policy tutorial](tutorials/26-signature-field-policy.md).

[Changelog](../../CHANGELOG.md) · [Verified coverage](coverage.md)
