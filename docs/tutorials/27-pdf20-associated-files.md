# 27. PDF 2.0, métadonnées Unicode et fichiers associés

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.6.2/examples/pdf20-associated-files.php)
génère une page PDF 2.0 avec police incorporée, métadonnées Unicode et CSV
incorporé. Le CSV est associé au document et à la page ; une liste de propriétés
MCAF nommée relie le contenu marqué au fichier. Ce sont de véritables objets PDF,
pas seulement un nom de fichier dessiné sur la page.

## Exécuter l'exemple

Depuis un checkout du core 0.6.2 avec ses dépendances de développement verrouillées :

```bash
php examples/pdf20-associated-files.php pdf20-associated-files.pdf
```

PHP 8.3 ou supérieur et le module optionnel `pdftoolkit/pdf-fonts` sont utilisés.
Le checkout installe ce module pour les exemples ; l'installation normale du core
ne le fait pas. La construction exécute le script et rend ses pages. L'aperçu
ci-dessous provient de ce PDF réel ; le télécharger permet d'inspecter les
fichiers associés dans un lecteur compatible.

## Encoder séparément le texte visible et les métadonnées

Les métadonnées de dictionnaire utilisent `TextString` avec
`Utf8TextStringEncoding`, qui écrit un BOM UTF-8 avant la valeur encodée. Ce
mécanisme de chaîne textuelle appartient à PDF 2.0. L’exemple conserve l’entrée
dépréciée `Info.Title` uniquement pour démontrer cet encodage et ne prétend pas
garantir une conformité PDF 2.0 complète. Il permet des métadonnées
hors PDFDocEncoding sans supposer que leurs octets UTF-8 sont déjà des codes
utilisables par une police.

Le texte visible des pages suit une autre construction. L'exemple lit la police
de démonstration Noto Sans avec le convertisseur optionnel, incorpore son programme
PDF, sélectionne une ressource de police et fournit des codes CID aux opérateurs
de texte. La CMap ToUnicode relie ces codes à Unicode. Ces objets restent
nécessaires même lorsque les métadonnées du fichier utilisent UTF-8.

## Fournir et décrire le CSV

L'application fournit les octets CSV à `EmbeddedFileStream`, avec le nom MIME
`text/csv` et la date source `2026-10-14T00:00:00Z`. Son nom PDF est
`F (donnees.csv)` avec le nom Unicode préféré `UF`, `données.csv`.
`EF.F` et `EF.UF` référencent le même flux. `EmbeddedFileBindings` relie une référence indirecte du flux au
dictionnaire `EF` de la spécification de fichier. Le nom et la description restent
des valeurs PDF explicites ; le core ne charge pas de fichier externe et
n'interprète pas ses lignes CSV.

`AssociatedFileRelationship` ajoute `AFRelationship /Data`, pour déclarer le
rapport entre le CSV et la présentation PDF. La relation exprime une sémantique,
pas une instruction d'exécution du fichier. La taille et la somme de contrôle
décrivent les octets sans certifier leur origine ni leur innocuité.

## Relier le document, la page et le contenu marqué

`AssociatedFiles` contient les spécifications de fichiers et
`AssociatedFilesEntry` écrit `/AF` sur le catalogue et la page. Ces propriétaires
réutilisent la même spécification au lieu de fabriquer des copies indépendantes
de la pièce jointe. Un arbre de noms peut rendre le fichier accessible séparément
de son association avec ces propriétaires.

L'association du contenu marqué utilise un dictionnaire nommé dans
`Resources.Properties` contenant `/MCAF` sous `AFData`, puis `/AF /AFData BDC … EMC` dans le
flux de contenu. Le modèle EC3 corrigé maintient la liste de propriétés comme
dictionnaire et garde les références indirectes de flux hors de la syntaxe de
contenu. Un tableau direct après `BDC`, une association vide ou un fichier sans `AFRelationship` échouent à la
validation native des associations prises en charge ; `DP`/`MP` ne peuvent pas remplacer la séquence.

## Choisir le catalogue PDF 2.0

L'exemple utilise le schéma `CatalogDictionaryTable29` propre à l'édition et un
`FileHeader` PDF 2.0 explicite. Le catalogue exige `Type /Catalog` et sa référence
vers l'arbre des pages ; l'édition sélectionnée conserve EC3 séparément de la
version produite. Les métadonnées UTF-8 et AF/MCAF nécessitent PDF 2.0 et sont
contrôlés selon la version effective, y compris les déclarations du catalogue
et les objets effectifs des révisions.

Le tableau 29 ISO1 décrit un nœud de pages ; il ne doit pas remplacer ce
catalogue ISO2. Un nouvel en-tête seul n'implémente pas toutes les règles PDF 2.0.

## Inspecter le PDF et garder les limites visibles

Ouvrir le document téléchargé dans un lecteur gérant les fichiers incorporés
et associés. Inspecter `/AF` du catalogue et de la page,
`AFRelationship /Data`, les octets du flux incorporé, le dictionnaire nommé
`MCAF`, l'en-tête PDF 2.0 et les métadonnées UTF-8. Comparer le texte visible
avec la police incorporée et la correspondance ToUnicode. Les contrôles
indépendants examinent ces octets et références, pas seulement le succès d'une
commande de génération.

Le package optionnel `pdf-reader` 0.2 lit la syntaxe PDF 1.0–2.0 et les chaînes UTF-8 PDF 2.0, sans reprendre les mécanismes de chiffrement du writer.
L'exemple est validé par des outils externes pour PDF 2.0. Cette leçon ne chiffre
pas le fichier et n'implémente pas R=6, les espaces de noms natifs,
DSS/horodatages, parties documentaires ni la conformité ISO 32000-2 complète.

## Références

Le [guide PDF 2.0](../pdf-2-0.md) explique les éditions, l'applicabilité et les
mécanismes restants. Pages physiques de source : chaînes textuelles 131–132 ;
catalogue 113–117 ; fichiers 149–152 ; fichiers associés 853–856 ; tableau MCAF
409a corrigé 1015. L'[original](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf) est conservé sans modification dans le dépôt public du core. Consulter aussi l'[accès sponsorisé officiel](https://pdfa.org/sponsored-standards/)
et l'[erratum public 374](https://github.com/pdf-association/pdf-issues/issues/374).

[Parcours des tutoriels](README.md) · [Couverture](../coverage.md)
