# Recipes and practical examples

[Tutorials](../tutorials/README.md) introduce format objects step by step. Recipes
combine these objects to build concrete presentations. Each recipe keeps layout
calculations in its script and explains the choices producing the result.

| Recipe | Result | Code |
| --- | --- | --- |
| [An explicitly drawn table](table.md) | Header, five rows, alternating backgrounds, grid and total. | [table.php](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/table.php) |

## Propose a recipe

A contribution can demonstrate a printed table of contents, chart, information
sheet or another composition. Choose a case small enough for readers to follow
the object graph and its operators.

1. Add a standalone script in the core's `examples/`, with reproducible demonstration data and an optional output path.
2. Comment the steps explaining objects, resources, references and coordinates. The script loads `vendor/autoload.php` and uses the checkout's API.
3. Add a guide in the documentation repository's `docs/recipes/`, with a command, a preview derived from the PDF, parameters to try and composition limitations. Credit the author and sources if the recipe comes from a contribution or existing work.
4. Add links to this index, inspect the PDF in a reader and run `composer check` in the core checkout. PHPStan also analyzes examples; CI runs every `examples/*.php` script and checks its PDF with qpdf. After publishing the package, update the source manifest and validate the central site build.

Recipes can demonstrate position calculations and repetition in PHP. The PDF
values, resources and instructions they produce remain model objects. A reusable
layout API can be developed in a separate library.

[Tutorial index](../tutorials/README.md) · [Back to the project](../../../README.md)
