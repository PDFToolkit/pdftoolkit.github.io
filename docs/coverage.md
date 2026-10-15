# Couverture par édition PDF

Les inventaires de dictionnaires ISO1, Adobe et ISO2 conservent des identités de
sources distinctes. Définitions, algorithmes natifs, relations documentaires et
conformité sont des dimensions différentes. L’inventaire complet des tableaux
n’établit pas toutes les conditions, opérations de rendu ou exigences de profils externes.

## Règles de source exécutables et corrections EC3 examinées

Le [guide des audits de source](source-audits.md) distingue les règles
intrinsèques exécutées de chaque édition, les corrections EC3 reliées aux
annotations exactes et les 65 corrections des errata Adobe classées. Les
registres versionnés conservent portée et preuves ; leur taille n'est pas un
pourcentage de conformité PDF. Un classement éditorial ou un lien vers une
définition ne vaut pas exécution d'un algorithme.

Le garde incrémental compare les révisions natives figées complètes et exige
leur provenance ainsi que les signatures historiques vérifiées. Le core 0.11
ajoute texte enrichi borné et valeurs indirectes exclusives au remplissage
Tx/Ch/Btn, avec remplacement complet des apparences normales. Il autorise des
modèles de page historiques sans annotations et conserve les annotations P3
listées. Les historiques UR3 chiffrés exigent une authentification explicite
par mot de passe ou certificat, toutes les clés nommées et une autorité par
mise à jour. La version PDF signée décide des droits de sauvegarde et des cas
PDF 2.0 `P=false`/absent. Verrous de champs, permissions de chiffrement et portée
applicative continuent de s'appliquer ensemble. Le
[guide des révisions protégées](protected-revisions.md) précise contrats,
intersections et écarts d'oracle ; le [guide de migration](migration-0.11.md)
décrit DParts, descripteurs Type3 et choix explicites de sémantique PDF 2.0.

Le [tutoriel de caviardisation](tutorials/36-applied-redaction.md) montre une
suppression réelle dans un graphe normalisé et un nouveau fichier sans
historique. WTPDF peut comparer le XML analysé à la valeur canonique d'un champ.
Ni ces opérations ni les corrections EC3 ne prouvent la conformité générale,
le rendu ou les propriétés demandant une évaluation humaine.

## Apparences de codes-barres ordonnées, relations du graphe et intégrité source

La construction native des codes-barres conserve la valeur de champ exactement
encodée, compresse la valeur entière avant répartition, lie les parties
ordonnées aux PMD sérialisées et construit `AP.N` sur tout le widget via un
encodeur d'image fourni explicitement. Le [guide du supplément Adobe](adobe-supplement.md)
explique valeurs vides/binaires, budgets, widget unique séparé ou fusionné et
ambiguïté de source. Cinq PDF, dix widgets et 45 contrôles de pixels utilisent
une image de test annoncée. Algorithmes PDF417/QR/Data Matrix, zones de silence
et comportement du scanner restent sous la responsabilité de l'encodeur.

Le [guide d'audit des sources](source-audits.md) ajoute appartenance effective
des annotations, relations réponse/popup, cibles d'actions distantes et
contrôles de mesures rectilignes. Les 84 tests et 132 assertions dédiés restent
séparés des règles intrinsèques des dictionnaires. Ils n'exécutent pas
d'actions, n'ouvrent pas les cibles distantes et n'implémentent pas toutes les
conditions d'annotations ou de mesures.

Le core 0.9.1 impose aussi `AP` aux véritables annotations PDF 2.0 des graphes
natifs ou conservés. Les exceptions sont un rectangle réduit à un point et
`Popup`/`Projection`/`Link` ; un rectangle horizontal ou vertical d'aire nulle
demande encore son apparence. Forms, états et `AS` de type nom sont contrôlés
sans refuser le cas licite d'un état non correspondant. Le registre source
inclut les corrections EC3 exactes approuvées #22 et #124. Projection interdit
séparément `AP` lorsqu'une dimension du rectangle est nulle. Huit PDF, onze refus
natifs et 28 contrôles indépendants de pixels exercent ce domaine ; aucune
apparence implicite n'est inventée.

WTPDF suit les véritables programmes de glyphes Type 3 natifs sélectionnés et
leurs fontes auxiliaires, avec la sémantique ISO2 des modes 3/7 et les
différences Poppler explicites. Les contrôles contextuels de dépréciation
distinguent `Recommendation` des erreurs et conservent les preuves opaques/de
contexte de fichier en attente. Ces ajouts ne certifient ni un programme de
fonte arbitraire ni la conformité WTPDF/PDF/UA.

Le lecteur 0.4 vérifie les MAC PDF sources autonomes ou attachés à une signature
avant d'interpréter le contenu protégé, sur les octets originaux et l'étendue
exacte du jeton. Son [guide MAC](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html)
distingue la politique compatible acceptant les entrées non protégées de
`RequirePdfMac`, l'authentification du fichier courant de la vérification de
chaque ancienne révision, et l'intégrité MAC de la validité mathématique des
signatures ou de la confiance des certificats. Le lecteur 0.5 ajoute
l'[authentification par clé publique](https://pdftoolkit.github.io/fr/modules/reader/public-key-authentication.html)
explicite Adobe.PubSec s3/s4/s5, des clés indépendantes par filtre et l'accès
EFOpen différé. Les droits effectifs viennent des payloads CMS authentifiés,
pas de `Encrypt.P` ; le MAC PubSec moderne utilise la clé DefaultCryptFilter authentifiée.

Le lecteur 0.4 traite aussi les valeurs nulles optionnelles de dictionnaires
comme absentes, y compris les références terminant sur un objet indisponible.
`ReadDocument::resolve()` suit les chaînes physiques de références indirectes
avec limites communes de profondeur et de cycles. PDF 2.0 autorise ces chaînes
hors flux d'objets ; un membre compressé contenant uniquement une autre référence
reste refusé. Les entrées MAC optionnelles nulles sont absentes ; les véritables
valeurs de sécurité non nulles conservent leurs obligations d'objets directs.
Ces règles n'impliquent ni parcours arbitraire du graphe ni réparation implicite
d'une source malformée.

Le lecteur 0.4.1 conserve les identités terminales `Encrypt`/`Root`/`Metadata`
du catalogue à travers ces chaînes. Les credentials de chiffrement restent
inchangés à la relecture ; la métadonnée implicitement claire reste limitée au
véritable flux du catalogue de type correct. Ses quatre cas d'alias supplémentaires
conservent le ciphertext original ; le [guide de sécurité](security.md) expose
leur validation indépendante et les limites des lecteurs de haut niveau.

Reader 0.6 expose les [révisions physiques](https://pdftoolkit.github.io/fr/modules/reader/revision-history.html)
et préfixes source exacts avec budgets cumulés. Ces vues restent non
authentifiées ; les relire avec les credentials et politiques d'intégrité
explicites pour accéder au contenu protégé. Lire l'historique ne vérifie pas
les signatures et ne fournit pas une `FileRevision` native au writer.

## ISO 32000-2:2020 EC3 et bundle complémentaire dans 0.7.1

Le [guide PDF 2.0](pdf-2-0.md) documente les objets propres à l’édition : tableaux
sur plusieurs pages, entrées fixes et variables, définitions communes et corrections
vérifiées. L’[inventaire ISO2](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-2020/coverage.json)
consigne les compteurs exacts et la revue sémantique/EC3 restante. Il ne fusionne
pas ISO1 et Adobe dans un pourcentage unique de conformité.

Le [guide du bundle](pdf-2-0-bundle.md) couvre onze sources conservées. Les mécanismes
exécutables comprennent l’authentification R=6, AES-GCM, SHA-3/SHAKE256, CMS avec
courbes nommées, PDF MAC, horodatages RFC3161, DSS/VRI, espaces de noms structurels,
inclusion ISO/TS 32005, déclarations XMP, métadonnées d’objets et de contenu marqué,
compensation du point noir, parties documentaires et enveloppes chiffrées.
Les mesures géospatiales comprennent systèmes de coordonnées, points de contrôle
appariés, viewports, matrices affines et nuages de points typés.
Les sorties initiales, incrémentales et linéarisées sont contrôlées à travers le
graphe réellement émis et les snapshots immuables des révisions.

Le [relevé de couverture par document](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-bundle/coverage.json)
relie fichiers d’implémentation, tests et oracles indépendants à chaque original.
Le [relevé WTPDF](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/coverage.json)
distingue échecs mécaniques, revue humaine et validation supplémentaire.
Son [inventaire d’exigences](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/requirements.json)
consigne chaque aspect étudié, clause source, frontière d’exécution et chemin de preuve.
Le vérificateur reproductible rejette clauses omises et fichiers de preuve absents.
Aucune certification WTPDF/PDF/UA-2 automatique ni conformité complète à la norme
de base n’est revendiquée. Le lecteur 0.3 ajoute l'authentification R=2–7 sur
activation explicite, les xrefs hybrides et d'autres filtres au périmètre PDF
1.0–2.0. Son [guide d'authentification](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/docs/authentication.md)
précise les filtres cryptographiques acceptés. Le lecteur 0.4 ajoute la frontière
MAC source décrite ci-dessus ; le lecteur 0.5 ajoute l'authentification
par clé publique source bornée. Ces mécanismes restent distincts de l'écriture et du rendu.

L’[original de la norme principale](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf)
et les onze nouveaux originaux restent inchangés dans le dépôt public du core,
avec identités de sources et pages physiques. Le fournisseur est la
[PDF Association](https://www.pdfa.org/sponsored-standards/). Les téléchargements
Adobe ci-dessous restent disponibles sans modification.

## Références conservées

| Document | Inventaire | Source |
| --- | --- | --- |
| ISO 32000-1:2008, PDF 1.7 | 756 pages ; 392 tableaux ; 263 tableaux de dictionnaires ; 1 405 classes d'entrée ; 73 opérateurs de contenu | [PDF32000_2008.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF32000_2008.pdf) |
| Supplément Adobe, niveau d'extension 3 | 140 pages ; 66 tableaux, dont 61 tableaux de dictionnaires | [adobe_supplement_iso32000.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/adobe_supplement_iso32000.pdf) |
| ISO 32000-2:2020 EC3, PDF 2.0 | 1 023 pages physiques ; inventaire des dictionnaires de base propre à l’édition et corrections EC3 vérifiées | [ISO_32000-2_sponsored_EC3.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf) |

Les fichiers originaux restent dans le dépôt du core. Les catalogues enregistrent leur
SHA-256 et les numéros de pages physiques ; les corrections d'interprétation
conservent la formulation imprimée et indiquent leur justification.

La [référence Adobe de 2006, ses errata et l'addendum de caviardisation](adobe-references.md)
sont également conservés, avec leur portfolio et un catalogue d'empreintes.
Ce sont des sources de comparaison et d'audit ; leur archivage ne modifie pas
les compteurs des deux inventaires actifs ni les statuts d'implémentation.

Les définitions `Redact` existent dans le tableau ISO 192. Le core 0.8.0 applique
aussi la caviardisation avec un processeur natif conservateur pour le contenu
normalisé pris en charge. Il retire les données touchées et canaux annexes et
écrit un nouveau graphe ; le contenu non pris en charge doit être normalisé
explicitement ou est refusé. Une annotation ou une mise à jour incrémentale
seule ne supprime toujours pas les données source.

Dans la version 0.5.2, la comparaison avec les errata Adobe corrige aussi le
`Count` de racine des signets tous explicitement fermés au premier niveau.
Le [guide des références](adobe-references.md) détaille cette règle et les
différences de contrats entre les éditions pour les digests de signature.

## Comment lire la couverture

L'[inventaire ISO](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-1/coverage.json) examine 98 familles de
mécanismes. L'[inventaire Adobe](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/adobe-supplement-iso32000/coverage.json)
distingue ses tableaux, algorithmes, prescriptions, notes de produit et standards
externes. Leur référence initiale est la version 0.3.0 ; les ajouts ultérieurs
doivent être accompagnés de fichiers d'implémentation et de preuves de validation.

Les dimensions sont distinctes :

- **Définition** : le dictionnaire et ses entrées ont des objets nommés, leurs
  types, exigences connues et références de source.
- **Écriture** : des objets exécutent réellement le mécanisme et produisent ses
  octets PDF, par exemple un flux LZW ou une table d'indices de linéarisation.
- **Règles sémantiques** : les plages, dimensions, conditions, héritages et liens
  entre objets sont contrôlés pour le domaine annoncé.
- **Validation** : des tests et, lorsque possible, une autre implémentation
  vérifient les documents produits. Un contrôle de syntaxe ne prouve pas à lui
  seul leur rendu, leur accessibilité ni leur validité cryptographique.

Un pourcentage unique mélangerait ces dimensions. Les inventaires donnent donc
les mécanismes vérifiés et le travail restant, plutôt qu'un chiffre de complétude.

## Constructions natives de la version 0.4.0

| Famille | Constructions et vérifications |
| --- | --- |
| Formulaires AcroForm | Arbres de champs, héritage, noms qualifiés, valeurs et flags, widgets séparés ou fusionnés, apparences et appartenance au catalogue réel. |
| FDF | Écriture native, hiérarchie des champs, export explicitement choisi et références de modèles de pages. |
| Structure logique et PDF balisé | Hiérarchie, rôles, classes, attributs, MCID/MCR/OBJR, ParentTree et IDTree ; vérification d'un document de plusieurs pages. |
| Couleurs, motifs et dégradés | Espaces calibrés et spéciaux, cellules tiling, sept dégradés et vrais flux binaires de maillages ; contrôles des octets et du rendu. |
| CMaps | Codespaces, correspondances CID et Unicode, plages, notdef, modes d'écriture et UseCMap ; extraction d'un encodage différent d'Identity-H. |
| Polices et chaînes | Type1, MMType1, TrueType, Type3, CIDFont et Type0 ; programmes déclarés, métriques horizontales et verticales, noms de sous-ensembles et encodages PDFDoc/UTF-16. |
| Images et transparence | Échantillons 1/2/4/8/16 bits, masques, Decode, Matte, groupes, états graphiques, mélanges, soft masks et trames ; les codecs JPX/JBIG2 restent externes. |
| Contenu optionnel | Groupes et appartenances, expressions de visibilité, configurations, usages et états propres au document. |
| Compression | LZW EarlyChange 0/1, transitions de taille et réinitialisations ; prédicteurs TIFF/PNG aux profondeurs 1/2/4/8/16, composés avec Flate ou LZW. |
| Chiffrement par mot de passe | Algorithmes ISO R=2/3/4, RC4 et AESV2, avec filtres et mises à jour incrémentales ; R=5 Adobe reste disponible explicitement. |
| Chiffrement par certificat | Groupes de destinataires CMS, clés de filtres distinctes et formats s3/s4/s5 ; contrôle des clés, données et interprétations de permissions. |
| Signatures | Réservation de Contents, fixation de ByteRange avant signature et remplissage sans déplacement ; vérification indépendante des trois formats ISO et de signatures successives. |
| Politiques de signature | Objets DocMDP, FieldMDP, droits d'usage, seeds et critères de certificat ; contrôles intrinsèques. L’orchestration des champs signés et les gardes natifs de provenance/delta sont implémentés. Le core 0.11.0 ajoute les opérations bornées formulaire/modèle/P3/UR3 du [guide dédié](protected-revisions.md) ; la classification générale reste ouverte. |
| Références hybrides | Table classique et flux xref auxiliaire, références historiques, objets comprimés et lecture par lecteurs anciens et récents. |
| Linéarisation | Ordonnancement natif, indices de pages et ressources partagées, vignettes et pièces jointes, objets comprimés, trois formats xref et variantes chiffrées. |

## Constructions natives ajoutées dans la version 0.5.0

| Famille | Constructions et vérifications |
| --- | --- |
| Historique exact | `FileRevision.previous`, snapshots des références remappées, dictionnaires réellement écrits et octets de flux encodés issus du même appel, avant chiffrement. |
| Révisions après linéarisation | Snapshot initial exploitable et mises à jour préservant les octets, les plages d'indices et `/Prev` ; 90 historiques, soit 270 PDF indépendants. |
| Liste libre et générations | Suppression, réutilisation, trous initiaux, générations retirées, saturation 65535 et restrictions ObjStm ; 90 historiques, soit 450 PDF indépendants sous les trois PHP. |
| Navigation | Labels, huit modes de destination et cadrages, espaces nom/chaîne distincts, articles et anneaux de beads, transitions et séquences ; 77 tests et un oracle de trois pages, 55 labels, 10 cadrages et trois révisions. |
| Fichiers et collections | Octets incorporés, Size/MD5, métadonnées Mac, EF/RF/CI, arbres de pièces jointes, schémas et items typés, préfixes et directions de tri ; 90 historiques, soit 180 PDF indépendants. |
| Politiques de champs signés | Seeds écrits, choix du backend/digest/certificat, verrous copiés, apparences effectives et preuves requises. Vérification mathématique du résultat avant finalisation ; huit PDF et neuf signatures RSA/DSA dans l'oracle permanent. |
| Permissions historiques de signature | Première certification, unicité, cardinalité UR, P1 historique, sélection FieldMDP des descendants et absence d'élévation de permission Adobe pour une nouvelle signature de champ. |
| Graphe effectif | Ressources, boxes et rotation héritées des pages, ordre et limites des arbres de noms, générations inexistantes et relations natives contrôlées sur les snapshots. |

Ces ajouts ne constituent pas une déclaration de couverture complète. La
classification générale des modifications de PDF externes, les changements
arbitraires de pages/contenus/ressources, les modèles contenant annotations ou
champs et les anciens handlers UR restent hors des opérations natives permises.
Les registres distinguent aussi les règles conditionnelles, graphes multimédias,
ressources et symbologies de codes-barres qui demandent d'autres processeurs ou
preuves. Les cas pris en charge disposent de tests et d'oracles ; ils ne
certifient pas toute révision ou tout document.

## Apparences modifiables corrigées dans la version 0.5.1

Les exemples AcroForm et de politique de signature délimitent leurs trois
apparences de texte variable par `/Tx BMC ... EMC`. Le cadre reste à l'extérieur ;
le texte, le clipping et les sélections de liste restent dans la partie
remplaçable. Sans ce marqueur, la procédure ISO autorise l'ajout du nouveau texte
à l'ancien flux, ce qui explique la superposition observée dans Acrobat Reader.

L'[oracle de régression](https://github.com/PDFToolkit/pdf/blob/v0.11.0/tools/validate_variable_text_appearances.py) analyse
les vrais opérateurs avec pypdf et exerce deux remplacements successifs pour
chaque apparence. Il vérifie la disparition des anciens textes, la conservation
des cadres et le cas négatif sans marqueur. Ces contrôles passent sous les trois
versions de PHP ; ils ne constituent pas une validation interactive d'Acrobat.
Les dessins statiques, boutons et signatures restent des apparences libres.

OpenType 0.3 fournit normalisation fvar/avar 1.0, métadonnées name/OS/2/STAT,
contours TrueType non hintés, programmes Type 2 CFF/CFF2 et variations
HVAR/VVAR/MVAR/gvar/cvar. La [couverture exhaustive des tables](https://pdftoolkit.github.io/fr/modules/opentype/coverage.html)
compte 27 périmètres implémentés, quatre partiels et 19 en attente. Les variantes
cmap restantes, avar 2.0, la VM TrueType, les tables couleur/bitmap/BASE/JSTF/MATH,
les conteneurs TTC/OTC/WOFF/WOFF2 et l'écriture/sous-ensemble de fontes restent
explicites. Rastérisation, shaping Unicode complet, bidi et retour à la ligne
sont des responsabilités de consommateurs séparés. `pdf-fonts` continue de
convertir seulement les fontes TrueType statiques prises en charge. Évaluer
une instance OpenType ne crée pas une fonte incorporable statique.

## Frontière du core

Le core construit les objets PDF et leurs mécanismes d'écriture. Les programmes
de police, profils ICC, données d'image encodées, certificats, messages CMS, XFA
ou médias sont fournis explicitement. Leurs traitements peuvent être confiés à
des composants dédiés ; ils ne sont jamais supposés réalisés parce que leur
dictionnaire existe.

La lecture d'un PDF externe appartient à
[pdf-reader](https://github.com/PDFToolkit/pdf-reader). La conversion de fichiers
image et de polices appartient à [pdf-images](https://github.com/PDFToolkit/pdf-images)
et [pdf-fonts](https://github.com/PDFToolkit/pdf-fonts). Le rendu, l'exécution
JavaScript, les moteurs XFA/3D/multimédia et la politique de confiance des
certificats demandent leurs propres processeurs ou standards.

[Couverture des définitions](specification.md) · [Supplément Adobe](adobe-supplement.md)
· [Sécurité](security.md) · [Tutoriels](tutorials/README.md)
