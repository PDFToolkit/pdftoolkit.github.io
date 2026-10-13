# Documentation contributor instructions

- This repository owns PDFToolkit's shared documentation, tutorials, site assets,
  build tools and GitHub Pages deployment at https://pdftoolkit.github.io/.
- Keep PHP production code, executable examples, fixtures, original Adobe PDFs
  and specification catalogues in their package repositories. Never move or
  rewrite an original reference PDF to maintain this site.
- Module guides remain next to their code and are rendered centrally from the
  selected releases. Keep their identities distinct from shared documentation.
- `resources/sources.json` selects published package versions and their exact
  peeled Git commits. Verify each tag and the installed module references;
  branches and unreleased package commits are not documentation source pins.
- Distinguish the documentation commit from every package commit in API links,
  prose provenance and the site manifest. Do not claim the site documents master.
- Keep every existing route, PDF example, source download and reference document
  accessible. The `/pdf/` project site provides HTML redirects with preserved
  queries/fragments and actual binary downloads, never HTML at a PDF URL.
- Validate the full API inventory, local links, anchors, package guide routes,
  rendered PDF previews, reference hashes, source links and compatibility site.
  Use real generated examples and the packages' independent PDF oracles.
- Keep commits atomic. Publish an annotated documentation tag and GitHub release
  after the exact candidate's build succeeds and the deployed site is verified.
  Do not change published tags. A package source-pin update is a documentation
  release; unchanged PHP packages do not need another release for it.
