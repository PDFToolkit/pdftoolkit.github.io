# Dériver du HTML sémantique depuis un PDF balisé

Une page PDF décrit quoi dessiner. Sa structure logique décrit le sens du contenu
et l'ordre de lecture. Le module optionnel `pdftoolkit/pdf-to-html` utilise cette
seconde description pour dériver du HTML selon **Deriving HTML from PDF 1.2**,
publication PDF Association conservée avec son code source.

Le dépôt [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html/tree/v0.1.2) a été
créé spécialement pour implémenter les règles de ce
[document de référence](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.2/resources/reference-documents/Deriving_HTML_from_PDF_1-2.pdf).
L'implémentation actuelle est **partielle** : le
[guide de couverture du module](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.2/docs/fr/coverage.md) distingue
les mécanismes testés et les lacunes techniques restantes.

Ce tutoriel exécute réellement `examples/01-derive-tagged-pdf.php` depuis la
version retenue du module. Le PDF d'entrée, toutes ses pages rendues, le HTML
obtenu, les diagnostics JSON et le PHP complet apparaissent ci-dessous. Le HTML
est produit pendant la construction du site et ne remplace pas un résultat par
une illustration écrite à la main.

## Installer le module optionnel

```sh
composer require "pdftoolkit/pdf-to-html:^0.1.2"
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
l'exemple sûr n'en exporte aucun.

Lire les diagnostics avant publication. Un modèle source représentant un
mécanisme ne garantit pas que l'adaptateur accepte tous les encodages de fontes,
opérateurs, filtres ou mécanismes de chiffrement des PDF externes.

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

Le profil par défaut n'exporte aucun runtime de script et n'autorise aucun
chargement de ressource distante. L'application peut fournir explicitement les
capacités de rendu/authentification ou activer le contenu fiable. Le pont optionnel
des champs/événements couvre validation, calcul et reset courants, sans implémenter
toute l'API Acrobat/ISO 21757-1. La matrice de couverture du module relie classes,
tests individuels, oracle HTML5/PDF indépendant et harness Node du runtime.

Les fragments MathML conservent un vocabulaire contrôlé de 192 noms d'éléments,
dont les MathML de présentation et de contenu. Préserver le balisage de contenu
ou élémentaire ne garantit pas son rendu natif par le navigateur ; le vocabulaire
étendu produit un diagnostic et le package ne fournit ni polyfill de rendu ni
évaluateur mathématique.

Lire l'[architecture du module](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.2/docs/fr/architecture.md),
sa [couverture](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.2/docs/fr/coverage.md)
et son [guide de sécurité](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.2/docs/fr/security.md)
pour distinguer modèle, fichier et runtime. Un HTML sémantique ne certifie pas
automatiquement l'accessibilité ou PDF/UA.
