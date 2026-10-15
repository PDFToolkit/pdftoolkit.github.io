# Migration to core 0.11

Core 0.11 extends protected native revisions and applies additional source-linked
EC3 corrections. Update construction policies explicitly when moving an existing
application to PDF 2.0. The source's effective header/catalog version remains the
writer's authority; a constructor option cannot override it.

## Replace document-part groups with explicit parents

`DocumentPart::addGroup()` becomes `addChildren($first, ...$others)`. Each call
appends siblings to one ordered, flat `/DParts` array. To represent a group,
construct a parent node and attach its children explicitly. Cycles, repeated
children and a page leaf with children are rejected, without attaching part of a
failed batch.

Move DPart XMP `Metadata` to `DocumentPartRoot`; DPart `Metadata` is now forbidden,
including retained incremental objects. Keep workflow data in `DocumentPartMetadata`
(`/DPM`). The root constructor accepts `NameType|MetadataEntry ...$entries` after
its root node and optional record level. Rename named `nodeNames:` arguments to
`entries:`; positional level-name arguments retain their meaning. DPM additionally
accepts decoded UTF-8 `NameType` values, including nested/indirect names. Keys still
follow XML Name rules. See [tutorial 28](tutorials/28-pdf20-metadata-declarations.md).

## Handle nullable Type3 names and versioned field policies

A Type3 `FontDescriptor` may omit `FontName`, so its `fontName` property is nullable.
Use `requiredName()` in code that requires a named descriptor. Other font subtypes
still require names. A retained Type3 `Name` and its descriptor name must agree.

Choose `ButtonFieldSemantics::Pdf20` for PDF 2.0 radio appearances without `Off`,
or retained pushbutton `V`/`DV`. Historical semantics remains the default.
Checkboxes still require `Off`; `AS` and the effective value remain consistent.
An explicit text-field `NullType` is preserved physically but treated as absent
when resolving inherited values.

Select `SignatureSeedSemantics::Pdf20` for PDF 2.0 seeds and supply `IntegerType`
for `V`. PDF 2.0's `LockDocument`, `AppearanceFilter` and capability 3 no longer
require an Adobe extension declaration. The historical default keeps the real-valued
capability and Adobe declaration rules. The frozen signing path checks the actual
edition again. Intrinsic EdDSA digest selection and the historical DSA/SHA1 rule
remain distinct; a backend must still prove its actual output.

## Authenticate every encrypted UR3 update

Pass one `PasswordUsageRightsAuthentication` or `CertificateUsageRightsAuthentication`
to each `UsageRightsAuthorization`, alongside the application granting authority
and selected operations. Password encoding/handler or certificate decrypter is
explicit. A caller-supplied file key, earlier successful update or credential's
mere presence supplies no authority.

```php
$authorization = new UsageRightsAuthorization(
    $authority,
    UsageRight::FillField,
    new CertificateUsageRightsAuthentication($recipientDecrypter),
);
```

Named crypt filters with different identities use `CryptFilterUsageRightsCredential`.
The native writer authenticates every declared key and intersects document-scope
permission words. This is stricter than the Reader's deferred attachment access.
Owner/public-key all-access never overrides UR, DocMDP, FieldMDP or application scope.
Creating a terminal signature field additionally needs `UsageRight::AddField`
and actual security permission for field creation, independently of signing.

Restrictive PDF 2.0 UR3 filling now requires signed `Document.FullSave`; `FillIn`
alone is insufficient. Do not rewrite the signed declaration to add that right.
PDF 2.0 `P=false`/absent follows its own semantics while retaining verified identity,
explicit application scope and all DocMDP/FieldMDP restrictions. The source's
signed version controls these rules, not a later catalog upgrade.

## Select rich text, indirect values and templates explicitly

Rich filling uses `RichTextFilling(new WtPdfXmlRichTextParser())` and paired `V`/`RV`.
The bounded parser checks plain/rich equivalence without network or XML entities.
Every affected widget requires a fresh complete normal appearance; caller-supplied
painting is not automatically certified to match the text. Historical resources,
geometry and locks remain fixed.

Indirect text strings/streams require exclusive frozen ownership by the exact
field entry and bounded decoding. `PageTemplateInstantiation` appends a proved
copy of an invisible historical `Names/Templates` page, with unchanged resources
and no field/annotation cloning. P1 refuses it; applicable UR requires
`SpawnTemplate` and saving rights. These grants do not permit arbitrary graph edits.

Keep the actual native `FileRevision` returned by writing/signing. Reader 0.6
[physical revision history](https://pdftoolkit.github.io/modules/reader/revision-history.html)
exposes source prefixes and identities without creating core modification authority.
Legacy UR, arbitrary external history import, general field-tree editing and
unrestricted new appearance resources remain unsupported. The
[protected-revision guide](protected-revisions.md) records exact checks, examples,
independent oracle disagreements and remaining boundaries.

[Coverage](coverage.md) · [Source audits](source-audits.md) · [Security](security.md)
