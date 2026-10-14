# Modèle de spécification et couverture

La source faisant autorité pour cette révision est `PDF32000_2008.pdf`,
conservé dans le dépôt du core : ISO 32000-1:2008, PDF 1.7. Le document
supplémentaire `adobe_supplement_iso32000.pdf` décrit Adobe ExtensionLevel 3 ;
sa [couverture et son catalogue de sources distincts](adobe-supplement.md)
préservent la différence entre définitions ISO, extensions Adobe et notes
d'implémentation Acrobat. La [référence Adobe PDF 1.7, ses errata et l'addendum
de caviardisation](adobe-references.md) conservés ont un catalogue d'archivage
distinct, comprenant le portfolio original et les relations de ses documents
incorporés. Ils servent à la comparaison et aux audits ciblés ; leur
conservation ne modifie pas les inventaires de définitions actifs et ne prouve
pas l'implémentation de toutes leurs procédures.
La série 0.5 du core et les versions 0.1.5 des modules optionnels nécessitent
PHP 8.3 ou supérieur ; les anciens tags 0.1 du core conservent leur exigence
PHP 8.5. Ces versions PHP sont indépendantes de la version du format PDF.
Implémenter PDF 2.0 demande une spécification distincte et des définitions
explicites propres à cette version.

La source contient 756 pages PDF, 823 entrées de plan, 370 tableaux numérotés
principaux et 22 tableaux d'annexes. Le catalogue recense les 392 tableaux et
les 73 tokens d'opérateur de flux de contenu, y compris l'ancien `F` et les
délimiteurs d'image inline `BI`, `ID` et `EI`.

Les 263 tableaux décrivant des entrées de dictionnaires, des paramètres ou des
entrées d'attributs produisent 263 classes concrètes de dictionnaires, 263
classes immuables de définitions de tableaux, 1 399 classes concrètes d'entrées
fixes et six classes concrètes d'entrées variables. Les identifiants de tableaux
restent dans les noms de classes pour distinguer les dictionnaires de noms
similaires et rendre chaque définition traçable. Les noms PDF sont sensibles
à la casse ; les noms de classes PHP ne le sont pas. Pour les noms en conflit
comme `/OP` et `/op`, le nom de classe généré contient l'écriture hexadécimale
de son nom PDF.

Chaque entrée accepte des objets PDF, avec une union PHP correspondant aux
types d'objets de la source. Les références restent des objets explicites.
Une référence indirecte est vérifiée par rapport au type de sa cible. Les
valeurs de flux exigent un `IndirectReference` ; l'appelant ne fournit jamais
un flux direct comme valeur de dictionnaire. Les noms `Type` fixes connus
sont validés. Les rectangles exigent quatre nombres directs. Les entrées
des flux de références croisées et les éléments de leurs tableaux `Index`/`W`
doivent rester directs.

Chaque définition est un objet composé de `SourceReference`, `Requirement`,
`ObjectTypeConstraint` et `EntryDefinition`. `TableDefinition` compose
explicitement les tableaux de dictionnaires communs. `Catalogue` est une
collection immuable construite par l'appelant. Il n'y a ni singleton, ni cache
partagé, ni registre global de services, ni recherche JSON à l'exécution.
Les fichiers JSON sont des inventaires de sources utilisés par les outils
de construction reproductible.

Les classes de dictionnaires permettent une construction progressive par
des opérations `with()` immuables. Leur sérialisation contrôle les entrées
obligatoires inconditionnelles. Les exigences conditionnelles, entrées héritées,
limites numériques, énumérations autres que les noms `Type` fixes, relations
entre dictionnaires et règles propres aux algorithmes sont conservées dans
la description de source, mais **ne sont pas toutes contrôlées automatiquement**.
Les objets spécialisés de document, page, police, flux de contenu et fonction
apportent des comportements et contraintes supplémentaires.

Il s'agit d'un inventaire et d'un modèle de construction objet de bas niveau.
Ce n'est pas une affirmation que chaque algorithme ou chaque document valide
permis par les 756 pages de la norme dispose d'un modèle sémantique implémenté
et vérifié indépendamment. La signature, le balisage, la compression, les
couleurs/dégradés et la linéarisation natifs disposent maintenant de modèles
exécutables et de validations indépendantes. Les variantes, contraintes et
processeurs externes restants sont suivis dans le [guide de couverture des
mécanismes](coverage.md) et son inventaire de sources. Les classes de
dictionnaires nommées n'implémentent pas les algorithmes à elles seules.
Le rendu, la conversion externe d'images/polices, l'exécution de scripts et
la lecture multimédia conservent des responsabilités distinctes.

Le [backend historique AES-256 révision 5](adobe-supplement.md) supplémentaire
implémente les algorithmes du supplément Adobe conservé, avec credentials,
permissions, SASLprep Unicode 3.2 et intégration au writer explicites. Ce
protocole ancien est sélectionné volontairement. Les handlers ISO R=2/3/4
et à clé publique s3/s4/s5 ont aussi des opérations de writer explicites.
AES-CBC n'authentifie pas le contenu du fichier.

Le supplément possède aussi une dérivation historique de clés R=2–R=4
validée séparément, un condensat ordonné des destinataires à clé publique,
la correspondance des unités 3D et la préparation des données/calcul de largeur
des modules de codes-barres. Leurs API précisent leurs entrées et limites
exactes. Les backends CMS natifs et les opérations à clé publique se composent
explicitement ; le rendu des médias et l'encodage des symbologies de codes-barres
demandent toujours des processeurs externes. Voir le [guide du supplément](adobe-supplement.md)
et son inventaire de couverture versionné pour le statut de chaque algorithme.

## Mécanismes implémentés au-delà du modèle syntaxique

Le core implémente les objets et mécanismes PDF décrits par la référence
Adobe/ISO. L'analyse externe TrueType, JPEG et PNG est fournie par des packages
optionnels ; la lecture des PDF existants est aussi un package distinct.
Les modules dépendent du core, qui n'a aucune dépendance de production vers eux.
Voir le [guide des frontières de packages et d'installation](packages.md).

| Mécanisme | Comportement exécutable | Limites explicites |
| --- | --- | --- |
| Polices PDF — core | Programmes de police et métriques explicites, polices simples et composites, encodages, largeurs CID horizontales/verticales, CMaps, UseCMap et correspondances Unicode. | Le core reçoit des programmes et valeurs normalisés ; l'analyse externe des polices, les sous-ensembles et la composition demandent leurs propres processeurs. |
| Conversion TrueType — pdf-fonts | Validation sfnt/glyf statique, cmap Unicode 4/12, métriques, programme CIDFont complet et fabriques de conversion produisant des objets de police du core. | Pas de collections de polices, CFF/polices variables, sous-ensembles de glyphes, écriture verticale, crénage ou composition de scripts complexes. Le CIDFontProgram dérivé retire cmap selon 9.9 et le DSIG invalidé. Les permissions d'incorporation de la police d'origine sont contrôlées. |
| Images PDF — core | Dimensions, disposition des échantillons, espaces couleur, Decode, stencils, masques par couleur/explicites/souples et déclarations de données image encodées explicites. | Les données encodées et leur sémantique couleur/alpha sont déclarées par l'appelant. Les codecs externes et l'inspection des fichiers appartiennent aux convertisseurs optionnels. |
| Conversion JPEG — pdf-images | Validation des marqueurs/frames/tables, JPEG grayscale/RGB huit bits baseline et progressif, et transformation Adobe CMYK zéro vers un DCTImage du core. Les octets DCT originaux sont conservés. | Aucun décodage entropique ni encodage JPEG ; le lecteur décode les coefficients. ICC, YCCK et sémantiques couleur ambiguës sont refusés. L'orientation EXIF n'est pas appliquée. |
| Conversion PNG — pdf-images | Contrôles CRC/cadrage/ordre, décodage zlib borné, les cinq filtres de scanline, échantillons grayscale/RGB/indexés/alpha huit bits et tRNS vers les objets d'échantillons du core. | PNG statique non entrelacé seulement ; autres profondeurs, APNG et profils couleur incorporés refusés. Les métadonnées couleur auxiliaires ne créent pas d'espaces PDF calibrés. Les limites d'import sont des objets explicites. |
| Révisions incrémentales | Snapshots et historique FileRevision exactement figés, ajouts/remplacements, listes libres chaînées, suppression/réutilisation, générations retirées et alias, offsets et Prev, xref classiques/stream/hybrides, variantes chiffrées et mises à jour après linéarisation initiale. | Révisions générées seulement. Le remplacement d'une valeur vivante conserve sa famille d'objet et son Type de dictionnaire ; une nouvelle identité réutilisant un numéro libre peut avoir un autre type. Les anciens octets demeurent, donc une update ne peut effacer un contenu confidentiel. |
| Navigation | Labels de pages, destinations explicites et nommées, calculs de cadrage, anneaux d'articles et ordre de dessin des pages, transitions et séquences de présentation. | Le graphe natif et l'arithmétique sont contrôlés contre le catalogue effectif ; un lecteur rend et anime leur présentation. |
| Fichiers et collections | Octets incorporés fournis, métadonnées Size/MD5, informations Mac, EF/RF/CI, arbres de noms de pièces jointes et schémas/items/tris typés de collections ; déclarations de flux externes. | Aucun chargement implicite du système de fichiers/URL, conversion de plateforme ou exécution d'interface de collection. |
| Politiques de champs de signature | Seeds/verrous écrits, choix réels de certificat/digest/backend/apparence, sortie vérifiée avant finalisation et permissions intrinsèques historiques de signature. | L'analyse complète et authentifiée des différences de révisions et l'autorité/intersection UR restent ouvertes ; horodatage, révocation et confiance PKI demandent des composants externes explicites. |
| Lecture de PDF externes — pdf-reader | Syntaxe des objets PDF 1.0–1.7, xref classiques et stream, révisions Prev, flux d'objets, résolution explicite des références, conservation des flux encodés et décodage borné Flate/ASCIIHex/ASCII85/RunLength avec prédicteurs TIFF/PNG huit bits. Le parcours ordonné de l'arbre de pages contrôle comptes, parents et identités uniques ; Resources, MediaBox, CropBox et Rotate effectifs conservent les objets PDF. Les flux Contents locaux à la page sont résolus séparément dans l'ordre. | Pas de PDF 2.0, documents chiffrés, XRefStm hybrides, réparation, interprétation du contenu, rendu ou extraction de texte. Les codecs inconnus peuvent être conservés encodés mais pas décodés. Le parcours des pages n'inspecte pas tous les contenus de ressources. L'inspection de Contents ne concatène ni ne décode les flux. La lecture n'implémente pas l'import ou le remappage dans le writer. |

Le writer initial émet des enregistrements libres pour chaque numéro d'objet
inutilisé inférieur à Size. Les sections incrémentales émettent les enregistrements
modifiés et les nouveaux trous libres, en conservant la chaîne de liste libre
précédente. CrossReferenceLimits limite Size cumulé à 100 000 entrées par défaut,
avant d'allouer les enregistrements des trous ; l'application peut fournir une
capacité explicite au writer. Les nouveaux objets ont une génération zéro,
tandis que le remplacement d'un objet vivant conserve sa génération. Une
suppression incrémente la génération libre, une réutilisation emploie cette
génération conservée, et la génération 65535 est permanente. Un numéro de la
liste libre ne peut créer ni un nouveau conteneur ObjStm ni un membre comprimé.

Les tutoriels sur les [polices incorporées](tutorials/09-embedded-font.md), les
[fichiers image](tutorials/10-image-files.md) et les
[mises à jour incrémentales](tutorials/11-incremental-update.md) expliquent leurs
graphes d'objets et incluent des documents exécutables. Aucun de ces mécanismes
n'ajoute de registre global à l'application ni de moteur de mise en page automatique.

## Reconstruire l'inventaire de sources

Utiliser Python avec `pypdf` et `pdfplumber` installés :

```sh
python tools/extract_spec.py
python tools/generate_specification.py
python tools/generate_specification.py --check
```

`extract_spec.py` vérifie la présence de tous les identifiants de tableaux
principaux de 1 à 370, extrait les cellules des tableaux bordés, contrôle la
liste complète des 73 tokens d'opérateur et consigne les problèmes d'extraction
non résolus dans `extraction-issues.json`. L'inventaire versionné n'a aucun
problème d'extraction non résolu. Il consigne l'empreinte SHA-256 du PDF source
et les numéros de pages physiques du PDF.

`generate_specification.py` produit des classes nommées et des objets de
définition immuables. Son mode `--check` compare les fichiers générés sans
les modifier. Seuls les fichiers PHP obsolètes portant le marqueur de ce
générateur dans ses deux dossiers générés peuvent être retirés pendant une
régénération. Les outils Python sont des outils de développement ; la
bibliothèque PHP n'a aucune dépendance Python à l'exécution.

Les sources générées et leur inventaire doivent être examinés ensemble.
Les corrections d'extraction sont ciblées et documentées dans l'outil : deux
noms de clés coupés sur plusieurs lignes et deux clés OPI dépassant leurs
cellules imprimées. Les noms variables restent variables ; des formulations
descriptives comme « Other keys » ne sont jamais produites comme clés PDF fixes.

`corrections.json` consigne les décisions explicites d'implémentation lorsque
la formulation source est incohérente. Dans le tableau 15, le qualificatif ISO
2008 de `/Prev` indique qu'il doit être indirect, tandis que
[Adobe PDF Reference 1.7, tableau 3.13](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.7old.pdf)
exige un entier direct. Cette implémentation conserve `/Prev` direct pour
permettre de localiser la section précédente de références croisées avant
la résolution des objets indirects. La description et le qualificatif originaux
sont conservés, et un objet `ImplementationCorrection` immuable expose la
justification et les preuves. C'est une décision d'implémentation documentée,
pas une affirmation d'erratum ISO officiel. Les qualificatifs négatifs comme
« shall not be an indirect reference » sont interprétés comme contraintes
d'objet direct sans modifier leur formulation source.

## Étendre la couverture sémantique

Ajouter un objet immuable spécialisé pour le concept normatif, sa clause
source exacte et les contraintes significatives sur ses valeurs et relations.
Composer les définitions d'entrées existantes plutôt que maintenir un second
catalogue de noms. Conserver des parseurs, encodeurs, compression, chiffrement,
signatures, écriture de documents et rendu distincts des objets de définition,
avec des dépendances explicites. L'analyse de formats externes appartient aux
modules optionnels ; les valeurs PDF normalisées et mécanismes restent dans
le core. Utiliser des lecteurs et validateurs indépendants pour tester les
octets émis, en complément de tests unitaires ciblant les cas invalides.
Le statut d'implémentation d'une entrée doit distinguer son modèle objet,
sa sérialisation, ses contraintes et son algorithme associé.
