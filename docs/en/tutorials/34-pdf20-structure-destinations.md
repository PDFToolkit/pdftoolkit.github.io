# 34. Navigate to a PDF 2.0 structure element

A page destination identifies where to display a page. A structure destination
identifies a logical element, such as a section, whose content determines the
page to display. These are separate PDF objects: choosing a semantic target does
not require the application to duplicate its page number in every action.

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/pdf20-structure-destinations.php)
constructs a tagged document with visible internal links, a structure target and
explicit page fallbacks. It also publishes a named destination with an `SD` entry.
The PDF preview shows the actual pages; support for following `SD` depends on the viewer.

## Run the example

From a core 0.7.1 checkout with its locked development dependencies installed:

```bash
php examples/pdf20-structure-destinations.php structure-destinations.pdf
```

The font program is embedded explicitly. The optional font converter prepares its
metrics and Unicode mapping; the core writes the PDF objects. No remote document
is opened while constructing these destinations.

## Separate the view from its target

`DestinationView` owns the fit name and its explicit coordinates. It reuses the
existing PDF destination rules: `Fit` needs no coordinates, while `XYZ`, `FitH`,
`FitV`, `FitR`, `FitB`, `FitBH` and `FitBV` retain their own arity and null rules.

```php
$view = new DestinationView(new NameType('Fit'));
$destination = new StructureDestination($section, $view);
```

Here `$section` is the actual `StructureElement`, linked into the document's
structure tree. The destination serializes its indirect reference followed by
the view, rather than substituting a page reference or a numeric page index.

## Resolve the element's actual page

`StructureDestination::page()` follows the element's children in their declared
`K` order. It descends into child elements and finds the first content item with
a page: a marked-content identifier, MCR or object reference. A child element
does not count merely because its dictionary has a `Pg` entry.

If there is no qualifying content item, the standard falls back to the document's
first page. Traversal is bounded and cycles are rejected. The same calculation
works against the effective graph of an incremental revision, so an unstaged
builder mutation cannot silently change the meaning of retained output.

`local()` exposes the corresponding local page destination for existing viewport
calculations. It resolves the semantic target explicitly; serialization still
retains the structure destination itself.
This native viewport adapter needs a native `PageObject`; use `page()` and the
effective graph directly when the retained page is a frozen generic dictionary.

## Supply SD and the fallback deliberately

`GoToDestination` preserves its existing page destination and accepts a separate
`structure:` destination. The action writes `D` and `SD` independently. A viewer
that understands structure destinations can use `SD`; the fallback `D` remains
an ordinary page destination.

`StructureDestinationEntry` adds `SD` to a named `DestinationDictionary`, alongside
its required local fallback. Names, name trees, actions and structure elements
keep their existing object identities. A semantic destination does not create a
second structure tree or invent an element ID.

## Keep remote IDs as bytes

`RemoteStructureDestination` receives an explicit `StringType` identifier and a
view. Remote and embedded-document actions identify the other document's
structure element through its ID; they do not carry a local object reference.
The library does not fetch that document or assume that its ID exists. Validate
the external file and its identifier in the application that supplies them.

Local graph validation requires PDF 2.0, checks the actual structure-tree member,
the view and the destination's context. It also checks generic dictionaries and
frozen replacements; replacing a native class does not remove these requirements.

## Check the emitted navigation

The independent structure-destination oracle uses pypdf and qpdf to inspect the
written actions, named destinations, structure references and page fallbacks.
The PHP regressions exercise local and remote forms, traversal order, fallback,
invalid contexts and retained revisions. The source is ISO 32000-2:2020 clause
12.3.2.3 and the associated action/destination dictionaries, retained in the
[original EC3 reference](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf).

[Tutorial path](README.md) · [Geospatial objects](33-pdf20-geospatial.md) · [Bundle guide](../pdf-2-0-bundle.md)
