# Appliquer une caviardisation et écrire un nouveau PDF

[English](../en/tutorials/36-applied-redaction.md) · [Français](36-applied-redaction.md)

Une annotation `Redact` désigne du contenu à retirer. Peindre un rectangle opaque
ne supprime pas le texte ou les images sous-jacents. L'addendum Adobe, pages
physiques 2–4, exige la destruction des données concernées et une apparence de
remplacement. Le core 0.8.0 introduit `SecureRedaction` pour un graphe d'objets
explicitement normalisé.

## Exécuter le véritable exemple

```sh
composer require "roukmoute/pdf:^0.9.1"
php examples/pdf17-secure-redaction.php redacted.pdf --source=original.pdf
```

Le deuxième argument optionnel écrit l'original dans un fichier séparé pour
comparaison. Le résultat caviardé ne l'incorpore jamais et ne lui ajoute aucune
révision. Le code PHP exécutable complet et les deux pages obtenues figurent ci-dessous.

## Comprendre l'entrée

L'exemple construit deux petites pages partageant la même image. La deuxième
contient un texte secret, un remplacement `ActualText` et une annotation de
caviardisation sur le texte et l'image secrets. Les métadonnées XMP du catalogue
contiennent aussi un secret. Un rectangle vert hors de la zone choisie permet
de vérifier visuellement la préservation du contenu.

La page se termine par une matrice de translation volontairement persistante.
Le processeur doit isoler la marque de remplacement de cet état graphique source
pour la placer dans les coordonnées de l'annotation.

## Construire l'opération explicitement

```php
use PDF\Document\Redaction\RedactionAnnotation;
use PDF\Document\Redaction\RedactionPageRequest;
use PDF\Document\Redaction\RedactionPlan;
use PDF\Document\Redaction\SecureRedaction;

$result = (new SecureRedaction())->apply(
    $catalog,
    new RedactionPlan(
        new RedactionPageRequest($page, new RedactionAnnotation($annotation)),
    ),
);
$result->writeTo($destination);
```

`$catalog`, `$page` et `$annotation` sont les objets réellement assemblés par
l'application. Le plan lie une annotation sélectionnée à sa page ; il ne parcourt
pas le système de fichiers et n'importe pas implicitement un document externe.
Le résultat immuable est écrit dans un nouveau fichier, avec un nouveau graphe
atteignable et aucune révision antérieure.

## Suivre ce qui est supprimé

Le processeur par défaut ne dispose pas d'un backend de géométrie fiable des
contours de fonte. Il supprime donc de manière conservatrice tous les objets
texte de la page sélectionnée. Les déclarations `Widths` ou `FontBBox` ne prouvent
pas qu'un texte est hors zone. Une implémentation explicite de
`RedactionFontGeometry` peut fournir la géométrie réelle pour une préservation plus fine.

Une image ou un Form touché est indivisible. L'image partagée contaminée est
supprimée des **deux** pages, y compris de son usage antérieur hors de la page
sélectionnée. Les rectangles vectoriels verts restent présents. Cette
sur-suppression volontaire évite qu'une ressource partagée conserve ailleurs
dans le résultat des données concernées.
La même règle suit les dépendances inverses via `Mask`, `SMask` et les Forms
imbriquées avant de reconstruire les pages finales. Une image conservée ne peut
pas retenir indirectement une image supprimée comme masque de transparence.

Le nouveau catalogue retire les annotations, métadonnées, formulaires/XFA,
pièces jointes, actions, signets, structure et canaux de texte alternatif. Les
ressources de rendu inutilisées sont éliminées. Le résultat ne préserve pas la
structure d'accessibilité de la source.
Les fontes conservées perdent les données descriptives telles que `CharSet`,
`FontFamily` et `Style`. Les dictionnaires propres à chaque contexte vérifient
les types des valeurs conservées : une chaîne cachée sous un champ numérique
est refusée.
Le core 0.8.1 vérifie aussi le domaine et le sous-type réels de la police. Une
police simple Type1 ou TrueType ne peut conserver des entrées superflues
`CIDSystemInfo` ou `DescendantFonts`. Une Type0 exige son véritable descendant
CID et un encodage compatible ; les identifiants CID légitimes restent dans ce
domaine. Les combinaisons invalides sont refusées avant tout résultat au lieu
de recopier des chaînes inutilisées dans la sortie.

## Produire l'apparence de remplacement

`QuadPoints` prévaut sur `Rect` pour les régions choisies. Les bornes des chemins
utilisent des enveloppes conservatrices des points de contrôle, les coordonnées
transformées et l'étendue du trait. L'exemple peint un remplacement noir avec
le texte blanc `REDACTED` répété et centré, selon une apparence par défaut explicite.
Si `RO` est fourni, ce Form de remplacement prévaut sur la couleur et le texte superposé.
Les bornes des rectangles utilisent leurs quatre coins transformés après
rotation ou cisaillement. Un tracé non peint terminé par `n` est également
retiré si sa géométrie récupérable traverse une région.

Le processeur ne conserve que des données normalisées prises en charge. Le chemin
d'image par défaut accepte des lignes exactes d'échantillons en couleurs device.
La conservation d'images encodées opaques, profils couleur ou programmes de fonte
complexes exige un `RedactionResourceSanitizer` explicite qui analyse et reconstruit
ces ressources. Une image opaque touchée peut être supprimée sans décodage.

## Respecter le périmètre des entrées acceptées

Le contenu opaque non pris en charge, les opérateurs inconnus, états graphiques
non normalisés, motifs, shadings, contenu optionnel, XObjects externes, clipping
texte et chemins traversant une limite de clipping sont refusés. Les budgets
d'instructions, de graphe, d'imbrication, d'images et de répétition sont explicites.
Ce processeur n'est pas un éditeur général de PDF externes arbitraires et ne
détecte pas la stéganographie dans le contenu conservé.

Le validateur indépendant lance qpdf, inspecte les objets atteignables et flux
décodés avec pypdf et rend les pages source/résultat avec Poppler. Il vérifie
l'absence des textes, images et métadonnées secrets, la préservation des vecteurs
verts, le placement du remplacement et l'unique révision de sortie. Ces contrôles
démontrent la destruction et le rendu de cet exemple normalisé ; l'application
doit aussi valider son domaine d'entrée et son processus de publication.
L'oracle de régression rend seize pages au total, dont quatre cas de rectangles
transformés et deux cas de dépendances Mask/SMask transitives. Le parcours des
dépendances compte aussi les arêtes répétées dans le budget d'instructions.

[Audits des sources](../source-audits.md) · [Sécurité](../security.md) · [Tutoriels](README.md)
