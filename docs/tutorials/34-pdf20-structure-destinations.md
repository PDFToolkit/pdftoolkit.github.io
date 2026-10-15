# 34. Naviguer vers un élément de structure PDF 2.0

Une destination de page indique où afficher une page. Une destination de structure
désigne un élément logique, par exemple une section, dont le contenu détermine
la page à afficher. Ce sont des objets PDF distincts : choisir une cible sémantique
ne demande pas de recopier son numéro de page dans chaque action.

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/pdf20-structure-destinations.php)
construit un document balisé avec des liens internes visibles, une cible de
structure et des destinations de page de repli explicites. Il publie aussi une
destination nommée portant une entrée `SD`. L’aperçu montre les véritables pages ;
la prise en charge de `SD` dépend du lecteur.

## Exécuter l’exemple

Depuis un checkout du core 0.7.1 avec ses dépendances de développement verrouillées :

```bash
php examples/pdf20-structure-destinations.php structure-destinations.pdf
```

Le programme de fonte est incorporé explicitement. Le convertisseur de fontes
optionnel prépare métriques et correspondances Unicode ; le core écrit les
objets PDF. La construction des destinations n’ouvre aucun document distant.

## Séparer le cadrage et sa cible

`DestinationView` possède le nom de cadrage et ses coordonnées explicites. Il
réutilise les règles des destinations PDF existantes : `Fit` ne prend aucune
coordonnée ; `XYZ`, `FitH`, `FitV`, `FitR`, `FitB`, `FitBH` et `FitBV` conservent
leurs propres nombres de paramètres et règles concernant les valeurs nulles.

```php
$view = new DestinationView(new NameType('Fit'));
$destination = new StructureDestination($section, $view);
```

Ici, `$section` est le véritable `StructureElement`, relié à l’arbre de structure
du document. La destination sérialise sa référence indirecte suivie du cadrage,
sans lui substituer une référence ou un indice numérique de page.

## Résoudre la véritable page de l’élément

`StructureDestination::page()` suit les enfants dans leur ordre `K` déclaré. Il
descend dans les éléments enfants et trouve le premier contenu ayant une page :
identifiant de contenu marqué, MCR ou référence d’objet. Un élément enfant ne
compte pas simplement parce que son dictionnaire possède une entrée `Pg`.

Sans contenu satisfaisant ces critères, la norme prévoit la première page du
document. Le parcours est borné et les cycles sont rejetés. Le même calcul
fonctionne sur le graphe effectif d’une révision incrémentale : une mutation de
builder non publiée ne change pas silencieusement le sens d’une sortie conservée.

`local()` expose la destination locale correspondante pour les calculs de cadrage
existants. La cible sémantique est résolue explicitement ; la sérialisation conserve
la destination de structure elle-même.
Cet adaptateur de cadrage natif demande un `PageObject` natif ; utiliser `page()`
et le graphe effectif directement pour une page conservée sous forme de dictionnaire générique figé.

## Fournir SD et le repli délibérément

`GoToDestination` conserve sa destination de page existante et accepte une
destination `structure:` séparée. L’action écrit indépendamment `D` et `SD`. Un
lecteur prenant en charge les destinations de structure peut utiliser `SD` ; le
repli `D` reste une destination de page ordinaire.

`StructureDestinationEntry` ajoute `SD` à un `DestinationDictionary` nommé, à côté
de son repli local obligatoire. Noms, arbres de noms, actions et éléments de
structure conservent leurs identités objet existantes. Une destination sémantique
ne crée pas un second arbre et n’invente pas d’identifiant d’élément.

## Conserver les identifiants distants en octets

`RemoteStructureDestination` reçoit un identifiant `StringType` explicite et un
cadrage. Les actions vers un document distant ou incorporé désignent son élément
de structure par son ID, sans référence vers un objet local. La bibliothèque ne
récupère pas ce document et ne suppose pas que l’identifiant existe. Valider le
fichier externe et son identifiant dans l’application qui les fournit.

La validation du graphe local exige PDF 2.0 et contrôle l’appartenance à l’arbre
de structure réel, le cadrage et le contexte. Elle contrôle aussi les dictionnaires
génériques et les remplacements figés : remplacer une classe native ne supprime
pas ces exigences.

## Vérifier la navigation émise

L’oracle indépendant des destinations de structure utilise pypdf et qpdf pour
inspecter actions, destinations nommées, références structurelles et replis de
page écrits. Les régressions PHP couvrent les formes locales et distantes, l’ordre
de parcours, le repli, les contextes invalides et les révisions conservées. La
source est la clause 12.3.2.3 d’ISO 32000-2:2020 et les dictionnaires d’actions et
destinations associés, conservés dans
l’[original EC3](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf).

[Parcours des tutoriels](README.md) · [Objets géospatiaux](33-pdf20-geospatial.md) · [Guide du bundle](../pdf-2-0-bundle.md)
