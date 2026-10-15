# Couverture par édition PDF

Les inventaires de dictionnaires ISO1, Adobe et ISO2 conservent des identités de
sources distinctes. Définitions, algorithmes natifs, relations documentaires et
conformité sont des dimensions différentes. L’inventaire complet des tableaux
n’établit pas toutes les conditions, opérations de rendu ou exigences de profils externes.

## Règles de source exécutées dans le core 0.8.0

Le [guide des audits de source](source-audits.md) distingue 197 règles intrinsèques
de dictionnaires exécutées (98 PDF 1.7, 99 PDF 2.0), quatre corrections EC3
examinées et un classement de 65 corrections couvrant toutes les pages d'errata
Adobe qui en contiennent. Ces nombres décrivent ces domaines précis, pas un
pourcentage de conformité PDF. Le placement natif des apparences et la sémantique
des indices de choix préservent l'édition et la correction applicables.

Le [tutoriel de caviardisation](tutorials/36-applied-redaction.md) démontre une
suppression conservatrice réelle dans un graphe normalisé et un nouveau fichier
à une révision. WTPDF peut comparer le texte enrichi XML analysé à la valeur
canonique d'un champ, sur activation explicite. Les annotations EC3 non examinées,
d'autres relations conditionnelles/de ressources, l'autorisation générale des
modifications DocMDP/FieldMDP/UR authentifiées, le rendu et les preuves externes
ou humaines de conformité restent des travaux explicites.

## ISO 32000-2:2020 EC3 et bundle complémentaire dans 0.7.1

Le [guide PDF 2.0](pdf-2-0.md) documente les objets propres à l’édition : tableaux
sur plusieurs pages, entrées fixes et variables, définitions communes et corrections
vérifiées. L’[inventaire ISO2](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/iso32000-2-2020/coverage.json)
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

Le [relevé de couverture par document](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/iso32000-2-bundle/coverage.json)
relie fichiers d’implémentation, tests et oracles indépendants à chaque original.
Le [relevé WTPDF](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/wtpdf-1.0/coverage.json)
distingue échecs mécaniques, revue humaine et validation supplémentaire.
Son [inventaire d’exigences](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/wtpdf-1.0/requirements.json)
consigne chaque aspect étudié, clause source, frontière d’exécution et chemin de preuve.
Le vérificateur reproductible rejette clauses omises et fichiers de preuve absents.
Aucune certification WTPDF/PDF/UA-2 automatique ni conformité complète à la norme
de base n’est revendiquée. Le lecteur 0.3 ajoute l'authentification R=2–7 sur
activation explicite, les xrefs hybrides et d'autres filtres au périmètre PDF
1.0–2.0. Son [guide d'authentification](https://github.com/PDFToolkit/pdf-reader/blob/v0.3.0/docs/authentication.md)
précise les filtres cryptographiques acceptés et refuse PDF MAC/authentification
par clé publique en entrée. Ces mécanismes restent distincts de l'écriture et du rendu.

L’[original de la norme principale](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf)
et les onze nouveaux originaux restent inchangés dans le dépôt public du core,
avec identités de sources et pages physiques. Le fournisseur est la
[PDF Association](https://www.pdfa.org/sponsored-standards/). Les téléchargements
Adobe ci-dessous restent disponibles sans modification.

## Références conservées

| Document | Inventaire | Source |
| --- | --- | --- |
| ISO 32000-1:2008, PDF 1.7 | 756 pages ; 392 tableaux ; 263 tableaux de dictionnaires ; 1 405 classes d'entrée ; 73 opérateurs de contenu | [PDF32000_2008.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf) |
| Supplément Adobe, niveau d'extension 3 | 140 pages ; 66 tableaux, dont 61 tableaux de dictionnaires | [adobe_supplement_iso32000.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/adobe_supplement_iso32000.pdf) |
| ISO 32000-2:2020 EC3, PDF 2.0 | 1 023 pages physiques ; inventaire des dictionnaires de base propre à l’édition et corrections EC3 vérifiées | [ISO_32000-2_sponsored_EC3.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf) |

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

L'[inventaire ISO](https://github.com/PDFToolkit/pdf/blob/v0.5.4/resources/iso32000-1/coverage.json) examine 98 familles de
mécanismes. L'[inventaire Adobe](https://github.com/PDFToolkit/pdf/blob/v0.5.4/resources/adobe-supplement-iso32000/coverage.json)
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
| Politiques de signature | Objets DocMDP, FieldMDP, droits d'usage, seeds et critères de certificat ; contrôles intrinsèques. L'orchestration et la comparaison des révisions autorisées restent ouvertes. |
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

Ces ajouts ne constituent pas encore une déclaration de couverture complète.
La comparaison générale des modifications authentifiées permises par DocMDP,
FieldMDP et UR reste ouverte : pages, contenu, ressources partagées, annotations,
valeurs héritées et instanciation de templates demandent une analyse propre.
Les autres priorités sont les familles d'annotations et leurs relations, les
autres règles de mesure 2D, les graphes multimédia/RichMedia, certaines règles de
fonctions et les procédures de préparation des apparences de codes-barres.
Les conditions, seuils de versions et ressources doivent aussi continuer à être
audités famille par famille. Les inventaires distinguent ces travaux des
constructions et preuves déjà livrées.

## Apparences modifiables corrigées dans la version 0.5.1

Les exemples AcroForm et de politique de signature délimitent leurs trois
apparences de texte variable par `/Tx BMC ... EMC`. Le cadre reste à l'extérieur ;
le texte, le clipping et les sélections de liste restent dans la partie
remplaçable. Sans ce marqueur, la procédure ISO autorise l'ajout du nouveau texte
à l'ancien flux, ce qui explique la superposition observée dans Acrobat Reader.

L'[oracle de régression](https://github.com/PDFToolkit/pdf/blob/v0.5.4/tools/validate_variable_text_appearances.py) analyse
les vrais opérateurs avec pypdf et exerce deux remplacements successifs pour
chaque apparence. Il vérifie la disparition des anciens textes, la conservation
des cadres et le cas négatif sans marqueur. Ces contrôles passent sous les trois
versions de PHP ; ils ne constituent pas une validation interactive d'Acrobat.
Les dessins statiques, boutons et signatures restent des apparences libres.

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
