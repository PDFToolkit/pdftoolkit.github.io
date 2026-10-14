# 30. Espaces de noms PDF 2.0 et vérification WTPDF

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-tagged-namespaces.php) construit une page avec une structure logique indépendante de son dessin. Il combine des rôles PDF 2.0, les types de table des matières propres à PDF 1.7 et un paragraphe personnalisé. Une police incorporée, des liens ParentTree réciproques et des métadonnées XMP rendent ces associations inspectables dans le fichier réel.

L’aperçu présente cinq lignes. Leur position ne crée pas leur sens : le script construit explicitement les éléments H1, P, TOC, TOCI et Reference qui permettent de les interpréter.

## Exécuter l’exemple

Depuis un checkout du core 0.7.0 avec ses dépendances de développement verrouillées :

```bash
php examples/pdf20-tagged-namespaces.php namespaces.pdf --audit-json
```

Le premier argument désigne le PDF de sortie. `--audit-json` écrit un rapport séparé sur la sortie d’erreur ; il ne mélange pas du JSON aux octets du PDF. Les options `--xref-stream` et `--hybrid` choisissent respectivement un flux xref et une section hybride. Sans ces options, le writer produit une table xref classique.

Le module optionnel `pdftoolkit/pdf-fonts` lit la police Noto Sans de démonstration. Le core reçoit ses objets PDF normalisés : programme incorporé, descripteur, métriques CID, correspondance CID/GID et CMap ToUnicode. Installer uniquement le core n’installe pas ce convertisseur.

## Qualifier le sens par un namespace

Dans PDF 2.0, le nom d’un type ne suffit pas toujours à exprimer sa sémantique. `StructureRole` associe ce nom à un objet `StructureNamespace` :

```php
$pdf20 = new StructureNamespace(StandardStructureNamespace::PDF20);
$pdf17 = new StructureNamespace(StandardStructureNamespace::PDF17);
$document = new StructureElement(
    new StructureRole(new NameType('Document'), $pdf20),
);
```

Chaque élément écrit `/S` pour son type et une référence indirecte `/NS` vers le dictionnaire de namespace. `StructureNamespaces` fournit au `StructureTreeRoot` les instances canoniques utilisées dans ce document. Deux objets portant le même identifiant de namespace ne sont pas interchangeables dans ce modèle : un jeu de namespaces possède une seule instance pour chaque identifiant.

Les types communs à PDF 1.7 et PDF 2.0 utilisent le namespace PDF 2.0 dans un arbre mixte. Certains types, dont TOC, TOCI et Reference, restent définis dans le namespace PDF 1.7. ISO/TS 32005 précise leurs relations de parenté avec les autres éléments. Le script conserve donc leurs namespaces distincts au lieu de renommer tous les types.

## Définir un rôle personnalisé sans registre global

Le namespace de démonstration `urn:pdftoolkit:example:report` contient le type `ReportParagraph`. Son mapping cible explicitement le P du namespace PDF 2.0 :

```php
$report = new StructureNamespace(
    'urn:pdftoolkit:example:report',
    new NamespaceRoleMap(new NamespaceRoleMapping(
        new NameType('ReportParagraph'),
        new StructureRole(new NameType('P'), $pdf20),
    )),
);
```

Le dictionnaire `/RoleMapNS` contient une cible de la forme `[/P référence-namespace]`. Un nom seul y désignerait le namespace PDF 1.7 par défaut, même si le mapping appartient à un autre namespace. La résolution transitive conserve cette distinction, détecte les cycles et possède une limite explicite d’opérations.

Le writer vérifie que les namespaces utilisés et ciblés appartiennent au jeu du document. La validation du graphe effectif contrôle aussi les dictionnaires génériques et les faits figés des révisions : fabriquer des entrées `/NS` à la main ne permet pas de contourner la version minimale PDF 2.0.

## Relier le dessin aux éléments logiques

Chaque ligne est entourée d’une séquence de contenu marqué avec un MCID. Ces nombres sont locaux au conteneur de contenu ; ils ne sont pas des identifiants globaux d’éléments de structure. La page porte `/StructParents 0`, qui désigne sa clé dans le ParentTree.

`PageMarkedContent` relie chaque MCID à son `StructureElement`. Le `StructureTreeRoot` dérive alors le ParentTree réciproque : MCID 0 vers le titre, 1 vers le paragraphe personnalisé, 2 vers la référence de table des matières, puis 3 et 4 vers les paragraphes suivants. Le même arbre porte les liens `/P` entre parents et enfants.

La table des matières ajoute une autre relation. Son élément Reference possède un tableau `/Ref` qui cible le H1. Cette référence structurelle ne crée pas une zone de lien cliquable ; le script ne construit aucune annotation Link. `addReference()` permet aussi de construire des citations réciproques entre un élément appelant et une note FENote lorsque le document en a besoin.

## Choisir les règles d’inclusion et leurs corrections

`StructureInclusionRules` applique les 53 lignes du tableau 5 d’ISO/TS 32005 aux rôles résolus. Il vérifie les types d’enfants autorisés, leurs bornes d’occurrence, l’héritage des contraintes à travers Part/Div/NonStruct et les assemblages Ruby/Warichu. L’exception prévue pour un arbre exclusivement PDF 1.7 reste distincte des règles d’un arbre mixte.

Le mode par défaut `Published2023` suit la source fournie. L’exemple choisit explicitement `StructureInclusionCorrections::Resolved336And440` : les résolutions de la PDF Association autorisent Sub dans Code et remplacent la cellule WP/Figure indéfinie `c` par `0..n`. Cette sélection ne prétend pas constituer une nouvelle édition de la norme. Les autres discussions d’errata ne sont pas appliquées implicitement.

## Distinguer déclaration et vérification

Le paquet XMP contient un `dc:title` avec les valeurs `x-default` et `fr`. Il contient aussi deux déclarations explicites de l’auteur pour ce petit exemple : ISO/TS 32005 et le niveau de réutilisation WTPDF. Une déclaration est une assertion ; sa présence ne prouve pas que son contenu est vrai.

Les identifiants WTPDF fournis par la spécification sont exactement :

```text
http://pdfa.org/declarations/wtpdf/#reuse1.0
http://pdfa.org/declarations/wtpdf/#accessibility1.0
```

Le script demande ensuite un audit distinct :

```php
$audit = (new WtPdfAudit())->inspect(
    $catalog,
    new EffectivePdfVersion($header, $catalog),
    WtPdfConformanceLevel::Reuse,
);
$audit->assertNoDetectedFailures();
```

L’audit ne crée aucune déclaration. Il distingue `Failed`, `HumanReviewRequired` et `AdditionalValidationRequired`. L’exemple ne présente aucun échec détecté, mais conserve les revues en attente. `assertNoDetectedFailures()` ne signifie donc pas « document certifié accessible ».

Les contrôles mécaniques portent notamment sur les namespaces, les tableaux réguliers avec cellules fusionnées, certaines relations de listes et de notes, les annotations, les métadonnées, les descriptions de fichiers incorporés et l’usage réel des polices. Ils distinguent une police rendue, dont le programme doit être incorporé, d’une police utilisée exclusivement avec le mode de rendu de texte 3. Ils vérifient aussi certaines correspondances CID/GID et ToUnicode.

Le choix sémantique des types, la pertinence d’une description, l’ordre de lecture voulu et le contexte d’un champ exigent une revue humaine. Les programmes de fonte, leurs droits d’incorporation, certaines métriques, la grammaire MathML et d’autres règles exhaustives exigent une validation complémentaire. Le [relevé détaillé](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/wtpdf-1.0/coverage.json) sépare ces limites des contrôles exécutés. Cet audit partiel ne constitue pas une certification WTPDF ou PDF/UA-2.

## Vérifier les octets générés

`tools/validate_pdf20_tagging.py` inspecte les références indirectes, le mapping personnalisé, le ParentTree, les MCID, Ref et le XML XMP avec pypdf et qpdf. Il vérifie aussi chaque glyphe montré dans cet exemple : présence de son GID, correspondance Unicode et accord entre largeur PDF et métrique du programme TrueType réellement incorporé. Poppler fournit une extraction de texte indépendante. Les trois formats xref sont exercés.

On peut modifier les textes, créer un second namespace personnalisé ou remplacer la table des matières par une liste. Chaque modification doit conserver les associations entre opérateurs, MCID, conteneurs, parents et types résolus. Le fichier visible et le rapport sont deux résultats complémentaires à examiner.

## Références

Les [sources du bundle conservées](https://github.com/PDFToolkit/pdf/tree/v0.7.0/resources/iso32000-2-bundle/documents) proviennent de la [PDF Association](https://www.pdfa.org/sponsored-standards/). Pages physiques utiles : ISO 32000-2, 739–744 pour les dictionnaires et namespaces, 809–810 pour les namespaces standards ; ISO/TS 32005, 9–13 pour les règles de mélange et 14–46 pour le tableau complet ; WTPDF, 9–10 pour les niveaux de conformité, 14–30 pour la structure, 32–49 pour les autres contraintes. Les empreintes et l’identité de chaque fichier figurent dans le catalogue du bundle.

[Parcours des tutoriels](README.md) · [Guide PDF 2.0](../pdf-2-0.md) · [Couverture](../coverage.md)
