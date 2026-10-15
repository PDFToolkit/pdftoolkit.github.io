# Règles de source, errata et corrections vérifiées

Une spécification archivée, une définition de dictionnaire et une règle exécutée
constituent trois preuves différentes. Le core 0.8.0 ajoute des contrôles issus
des sources au modèle de dictionnaires et consigne les corrections effectivement
examinées. Les PDF originaux restent inchangés dans `resources/reference-documents/`.

## Exécuter les relations entre entrées

Les deux inventaires portent désormais **197 règles sémantiques intrinsèques** :
98 pour PDF 1.7 et 99 pour PDF 2.0, réparties sur 33 tableaux de chaque édition.
Un tableau expose des objets `SemanticRule` immuables, qui conservent leur
identifiant, leur source et leur `DictionaryConstraint` typé. Les dictionnaires
dérivés héritent des règles applicables. `SchemaDictionary::validate()` et la
sérialisation les exécutent ; leur simple présence dans un inventaire ne suffit pas.

Les contrôles concernent les domaines numériques et dimensions des tableaux,
les entrées/sorties des fonctions, l'alignement des filtres et `DecodeParms`, les
plages et objets directs des flux xref, les couleurs calibrées/ICC, les
échantillons et masques d'image, la géométrie des annotations et les options de
choix. Ils portent sur le domaine déclaré du dictionnaire ; l'interprétation des
ressources et toutes les conditions documentaires restent distinctes.

Les [règles PDF 1.7](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-1/semantic-rules.json)
et [règles PDF 2.0](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-2-2020/semantic-rules.json)
conservent leurs tableaux et pages physiques. Les générateurs reproduisent les
définitions PHP à partir de ces ressources vérifiées.

## Conserver la correction EC3 exacte

Le [registre de vérification EC3](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-2-2020/ec3-semantic-reviews.json)
relie chaque annotation examinée à l'empreinte du document conservé, sa page
physique, son identité et son fil d'approbation. Un outil vérifie ces liens.
Ces quatre corrections ne constituent pas une revue de toutes les annotations EC3.

| Correction examinée | Comportement implémenté |
| --- | --- |
| #246, page physique 81 | Les entrées communes de flux dans un xref sont récursivement directes ; les données externes `F` sont exclues. Les références `Root` et `Encrypt` du trailer gardent leurs propres règles. |
| #403, page physique 81 | Les flux xref refusent `Metadata` et `AF`. |
| #444, pages physiques 506–507 | `Path` prévaut sur `Vertices` dans une annotation ; les sommets sont ignorés et leur présence simultanée n'est pas une erreur. |
| #468, page physique 558 | Les indices de choix PDF 2.0 sont possibles sans `MultiSelect`. Des libellés différents partageant une valeur exportée imposent les indices. Une valeur `V` sous forme de tableau ne suffit plus à les imposer. |

Les trois premiers fils examinés se terminent au statut completed ; #468 est
accepted. Le registre conserve cette distinction. La construction native
`ChoiceField` choisit explicitement l'édition avec `ChoiceIndexSemantics::Pdf17`
(par défaut) ou `ChoiceIndexSemantics::Pdf20Ec3`. Cette dernière exige une version
PDF 2.0 effective. Pour migrer les arguments positionnels, passer cette enum avant
les arguments `Entry` variadiques, ou utiliser les arguments nommés. Voir le
[tutoriel des formulaires](tutorials/14-acroform-fields.md).

## Appliquer le placement corrigé des apparences

`AnnotationAppearanceTransform` calcule la boîte transformée de l'apparence à
partir des quatre coins, la matrice d'ajustement au rectangle de l'annotation et
la matrice effective. Rotation et cisaillement participent donc à l'ajustement.
La composition respecte l'ordre corrigé **Matrix × A**, qui n'est pas commutatif.
Une étendue source dégénérée est refusée ; une destination de taille nulle peut
se réduire à des coordonnées finies. Le choix de l'apparence, des bordures et les
relations entre annotations restent des responsabilités distinctes.

L'écriture refuse aussi un tableau `Contents` vide sur une page. Omettre
`Contents` pour une page sans flux de contenu, ou fournir un flux explicitement vide.

## Examiner les errata Adobe sans confondre les éditions

Le [registre des errata Adobe](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/adobe-references/errata-review.json)
classe **65 corrections**, couvrant toutes les pages physiques portant des
corrections, de 3 à 18, du document de 18 pages conservé. Trente et une entrées
renvoient à des mécanismes natifs, dont certains existaient avant cette version.
Les autres décrivent des modifications éditoriales, opérations du consommateur,
comportements d'anciens lecteurs, formats externes, définitions ou mécanismes
partiellement implémentés.

Un classement exhaustif ne constitue pas une implémentation exhaustive. Par
exemple, la suppression en 2007 du drapeau de seed `DigestMethod` ne doit pas
effacer le contrat distinct de l'extension Adobe level 3 ultérieure. Le registre
préserve les identités des sources et leurs éditions applicables.

## Comprendre les limites restantes

Le core 0.8.1 ajoute une garde conservatrice à chaque chemin d’écriture
incrémentale native. Elle exige la provenance réelle des révisions émises et
un historique de signatures vérifié, puis classe toutes les différences pour
la signature terminale ou la maintenance DSS/horodatage PDF 2.0. Les restrictions
de champs restent applicables. Le remplissage général, les annotations et
l’autorité UR ne se déduisent pas de P2/P3 et sont refusés sans classification.
La [revue de sécurité](security.md) décrit la migration depuis les finalisations
opaques ou snapshots fournis et la frontière PKI.

La [couverture](coverage.md) et les registres recensent toujours des annotations
EC3 non examinées, d'autres relations conditionnelles/de ressources et une
autorisation incomplète des différences de révision DocMDP/FieldMDP/UR
authentifiées. Le rendu, les sémantiques des fontes et codecs externes, la
confiance des certificats et l'évaluation humaine de l'accessibilité demandent
leurs propres preuves.

L'addendum Adobe de caviardisation dispose désormais d'un processeur natif
conservateur pour un graphe explicitement normalisé. Son
[tutoriel dédié](tutorials/36-applied-redaction.md) explique la suppression, les
ressources partagées, le nouveau fichier et les entrées refusées. WTPDF propose
aussi une comparaison XML native optionnelle du texte enrichi, décrite dans le
[guide du bundle](pdf-2-0-bundle.md) ; ces ajouts ne certifient pas des fichiers arbitraires.

[Couverture par édition](coverage.md) · [Références Adobe](adobe-references.md) · [PDF 2.0](pdf-2-0.md)
