# Dériver du HTML sémantique depuis un PDF balisé

[English](../en/tutorials/35-derive-html.md) · [Français](35-derive-html.md)

Une page PDF décrit quoi dessiner. Sa structure logique décrit le sens du contenu
et l'ordre de lecture. Le module optionnel `pdftoolkit/pdf-to-html` utilise cette
seconde description pour dériver du HTML selon **Deriving HTML from PDF 1.2**,
publication PDF Association conservée avec son code source.

Le dépôt [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html/tree/v0.2.1) a été
créé spécialement pour implémenter les règles de ce
[document de référence](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/resources/reference-documents/Deriving_HTML_from_PDF_1-2.pdf).
La version **0.2.1** distingue les règles exécutées, les décisions de sécurité,
les adaptations nécessaires au navigateur et les capacités fournies par
l'application. Le [registre des exigences](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/requirements.md)
relie les clauses du document aux décisions et aux tests ; le
[guide de couverture](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/coverage.md)
précise les entrées acceptées et les preuves indépendantes.

Ce tutoriel exécute réellement `examples/01-derive-tagged-pdf.php` depuis la
version retenue du module. Le PDF d'entrée, toutes ses pages rendues, le HTML
obtenu, les diagnostics JSON et le PHP complet apparaissent ci-dessous. Le HTML
est produit pendant la construction du site et ne remplace pas un résultat par
une illustration écrite à la main.

## Installer le module optionnel

```sh
composer require "pdftoolkit/pdf-to-html:^0.2.1"
```

Cette commande installe le core et le lecteur comme dépendances. Une application
utilisant seulement le core n'acquiert pas de conversion HTML. PHP 8.3+ avec DOM
et mbstring est nécessaire.

## Fournir le PDF et conserver des étapes explicites

L'exemple exécutable reçoit les chemins d'entrée et de sortie :

```sh
php examples/01-derive-tagged-pdf.php tests/Fixtures/tagged.pdf _build/derived.html
```

L'application lit le fichier choisi et fournit ses octets à `DocumentReader`.
`ReadPdfSource` parcourt la structure logique et les contenus acceptés pour
construire un `TaggedDocument`. Il distingue structure, texte Unicode, propriétés
et annotations plutôt que d'inférer un document à partir de coordonnées.

## Dériver le document et examiner les diagnostics

`HtmlDeriver` résout rôles et namespaces, dérive attributs et contenus puis
sérialise le HTML sémantique. Le résultat expose explicitement HTML, CSS,
ressources et diagnostics. Le script écrit la sortie choisie et décrit son
opération en JSON. L'application choisit elle-même stockage et publication.

Le script écrit aussi **chaque ressource retournée à côté du HTML** et indique
son nom, son type et son SHA-256. Conserver ces fichiers avec le HTML lors d'une
copie. Dans l'application, écrire explicitement `$result->assets` ou adapter les
URL des ressources de manière cohérente. Les scripts fiables, s'ils sont activés
volontairement, deviennent des ressources `pdf-script-<sha256>.js` externes ;
l'exemple 01 présenté ici n'en exporte aucun.

Lire les diagnostics avant publication. Un modèle source représentant un
mécanisme ne garantit pas que l'adaptateur accepte tous les encodages de fontes,
opérateurs, filtres ou mécanismes de chiffrement des PDF externes.

## Comprendre les règles exécutées et choisir un profil

Les tests vérifient notamment les associations inverses `ParentTree`, les
namespaces, les remplacements `ActualText`, les relations entre en-têtes et
cellules de table et la priorité des attributs HTML/CSS explicites. Un `Lbl`
imbriqué dans un `Form` reste associé au bon champ ; l'identifiant de navigation
`PDF-Page-X` identifie le parent du contenu effectivement dérivé pour cette page.
Les pages sans contenu conservé produisent un diagnostic, sans recevoir le
contenu d'une autre page.

Le choix du profil détermine les capacités à fournir :

| Besoin | Construction explicite |
| --- | --- |
| Réutiliser titres, texte, tableaux et images | Le profil sémantique par défaut et l'examen des diagnostics. |
| Conserver l'apparence complète d'une figure | `preferVisualFigures: true` et un `ContentRenderer` utilisant le moteur de votre application. |
| Restaurer certains champs à leur valeur PDF par défaut | `FormActionPolicy(allowReset: true)`, sans activer les scripts PDF. |
| Exporter l'ECMAScript incorporé d'un document fiable | `allowActiveContent: true`, après décision de confiance de l'application. |

Une lecture stricte refuse les associations inverses incohérentes. La lecture
permissive les signale ; elle ne désactive ni les contrôles de cycles ni les
budgets. Les PDF chiffrés nécessitent une capacité d'authentification explicite,
et le lecteur HTML destinataire doit appliquer les permissions vérifiées.
Le [guide des politiques](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/policies.md)
explique ces objets et leurs responsabilités.

## Exporter une figure et fournir le moteur de rendu

L'[exemple 02](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/examples/02-export-figure.php)
lit un PDF balisé, trouve une `Figure` et transmet son `ContentGroup` à
`GraphicPdfExporter` :

```sh
php examples/02-export-figure.php tests/Fixtures/tagged.pdf figure.pdf
```

L'exporteur construit en mémoire un véritable PDF isolé d'une page. Il conserve
les ressources, les transformations, le clipping et l'avancement du texte dont
la figure dépend, tout en retirant les peintures non sélectionnées. La CLI écrit
`figure.pdf` et affiche sa page source, ses dimensions en points et son SHA-256.
Le document de rendu ne contient pas les actions du catalogue, l'AcroForm ou les
scripts du document source.

Un XObject Form peut aussi être référencé directement par un `OBJR`, sans appel
`Do` dans une page. La version **0.2.1** conserve alors le clipping de son `/BBox`
dans les coordonnées locales du Form, y compris avec une matrice cisaillée, et
son groupe de transparence `/Group`. Sa `/Matrix` n'est appliquée qu'une fois.
Si vous fournissez un viewport explicite, il utilise les coordonnées de la page :
il ne reçoit pas une seconde fois la matrice du Form. L'[oracle de pixels
indépendant](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/tools/validate_graphics_context.py)
compare les rendus Poppler pour vérifier le clipping et la transparence, au-delà
de la seule présence de ces entrées dans le PDF exporté.

Pour obtenir une image dans le HTML, fournissez un objet implémentant
`GraphicsRasterizer::rasterize(RenderingDocument): ImageContent`. Cet objet reçoit
le PDF isolé et renvoie les octets PNG, JPEG ou GIF produits par votre moteur :

```php
use PDF\Html\DerivationPolicy;
use PDF\Html\HtmlDeriver;
use PDF\Html\PdfToHtml;
use PDF\Html\Rendering\RasterContentRenderer;
use PDF\Reading\FileBytes;

// $rasterizer est l'objet GraphicsRasterizer fourni par l'application.
$renderer = new RasterContentRenderer($rasterizer);
$converter = new PdfToHtml(deriver: new HtmlDeriver(
    policy: new DerivationPolicy(preferVisualFigures: true),
    renderer: $renderer,
));
$result = $converter->convert(new FileBytes($pdfBytes), 'chart.pdf');
```

`RasterContentRenderer` relie l'exporteur et ce moteur ; il conserve les dimensions
logiques de la fenêtre de rendu indépendamment de la résolution du raster. Le profil
visuel demandé échoue explicitement si le moteur manque ou refuse le groupe.
L'application choisit son installation, son isolation et ses limites d'exécution.
Voir le [guide des graphiques](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/graphics.md)
pour les programmes `GraphicProgram` conservés et les contrôles de pixels avec
Poppler.

## Restaurer un groupe de champs sans exécuter les scripts PDF

L'[exemple 03](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/examples/03-safe-form-reset.php)
construit un modèle source objet et produit un formulaire HTML autonome :

```sh
php examples/03-safe-form-reset.php safe-form-reset.html
```

Le champ `Person.Name` commence avec « Grace Hopper » comme `/V` et possède
« Ada Lovelace » comme `/DV`. Le bouton sélectionne le groupe `Person` :

```php
use PDF\Html\Forms\FormActionPolicy;
use PDF\Html\Forms\ResetFormAction;

$resetAction = new ResetFormAction(['Person']);
$policy = new \PDF\Html\DerivationPolicy(
    formActions: new FormActionPolicy(allowReset: true),
);
```

Dans le script complet, cet objet `ResetFormAction` est porté par le champ du
bouton. Sa sélection inclut `Person.Name` et les autres descendants de `Person`,
sans inclure `Personality.Name`. `exclude: true` inverse la sélection ; une liste
vide explicite ne signifie pas « tous les champs ». Un `/DV` absent efface la
valeur au lieu de restaurer le `/V` initial.

Cette politique exporte uniquement le runtime de formulaire construit par la
bibliothèque. Les scripts PDF du document, des pages et des widgets restent
désactivés ; les soumissions restent désactivées également. L'exemple écrit le
JavaScript retourné à côté du HTML. Conserver les deux pour essayer le reset dans
votre navigateur ; l'aperçu sandboxé de ce site n'exécute aucun runtime.

## Comparer le sens plutôt que la mise en page

Examiner titres, paragraphes et ordre de lecture dans l'aperçu HTML, puis les
comparer au PDF. Redistribution du navigateur et pagination PDF ont des buts
distincts. Le module n'infère pas de structure absente, ne fait pas d'OCR et ne
promet pas une reproduction au pixel. Le sandbox de l'aperçu n'autorise ni
exécution de script ni soumission de formulaire.

L'image rouge de la fixture contient un seul pixel d'échantillonnage, mais elle
est peinte sur **20 points PDF** de côté. L'adaptateur suit sa matrice de
transformation et produit **27 × 27 pixels CSS** après arrondi, selon 96 pixels CSS
pour 72 points PDF. Il conserve ainsi la taille logique sans confondre échantillons
et taille dessinée, ni reproduire chaque opération de positionnement/clipping.

Le profil par défaut n'exporte aucun runtime et n'autorise aucun chargement de
ressource distante. Activer le reset propre à la bibliothèque est distinct
d'autoriser l'ECMAScript PDF. Le pont optionnel des champs/événements couvre
validation, calcul et événements de pages testés, sans implémenter toute l'API
Acrobat/ISO 21757-1. Le registre des exigences et la matrice de couverture relient
classes, tests individuels, oracles HTML5/PDF et contrôles du runtime avec Node.

Les fragments MathML conservent un vocabulaire contrôlé de 192 noms d'éléments,
dont les MathML de présentation et de contenu. Préserver le balisage de contenu
ou élémentaire ne garantit pas son rendu natif par le navigateur ; le vocabulaire
étendu produit un diagnostic et le package ne fournit ni polyfill de rendu ni
évaluateur mathématique.

Lire l'[architecture du module](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/architecture.md),
sa [couverture](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/coverage.md)
et son [guide de sécurité](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/docs/fr/security.md)
pour distinguer modèle, fichier et runtime. Un HTML sémantique ne certifie pas
automatiquement l'accessibilité ou PDF/UA.
