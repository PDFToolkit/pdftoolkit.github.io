# Spécifications complémentaires PDF 2.0 : objets, algorithmes et vérifications

Le core **0.7** complète les fondations PDF 2.0 avec les spécifications
distribuées par la [PDF Association](https://www.pdfa.org/sponsored-standards/).
Les mécanismes restent des objets PDF explicites. L’application choisit la
version du fichier, les algorithmes, les espaces de noms, les métadonnées, les
relations et sa politique de vérification. Aucun registre global ni conversion
implicite d’un fichier externe n’intervient.

## Périmètre par document

| Document | Mécanismes exécutables | Vérifications et limites |
| --- | --- | --- |
| ISO 32000-2:2020 EC3 | Inventaire des dictionnaires propre à l’édition, encodages textuels, fichiers associés, R=6, espaces de noms, parties documentaires, enveloppes chiffrées, DSS et horodatages | 306 tableaux de dictionnaires et 1 709 objets d’entrées ; corrections EC3 sélectionnées et limites sémantiques restent distinctes. |
| ISO/TS 32001:2022 EC3 | SHA3-256/384/512 et SHAKE256 fixe de 64 octets ; déclaration d’extension ISO et objets de sélection du condensat | Vérifications indépendantes des condensats et CMS ; la suppression EC3 de la clause 5.1.3 est respectée au lieu d’étendre la règle barrée sur les références de signature. |
| ISO/TS 32002:2022 EC3 | Courbes nommées P-256/P-384/P-521 et Brainpool, Ed25519/Ed448, combinaisons exactes courbe/condensat et construction CMS | Vérification indépendante de 23 combinaisons. La confiance dans le certificat et sa révocation relèvent de la politique applicative. |
| ISO/TS 32003:2023 | AES-GCM/AESV4 avec V=6/R=7, étiquette d’authentification, séquence de nonces par clé et algorithmes d’authentification R=6 | pyHanko déchiffre les fichiers natifs ; un contenu chiffré altéré est refusé. AES-CBC R=6 reste un choix distinct. |
| ISO/TS 32004:2024 | KDFSalt, bit de permission 13, HKDF, enveloppement de clé AES, CMS AuthenticatedData, MAC autonome ou attaché à une signature | pyHanko vérifie les fichiers initiaux, incrémentaux et linéarisés ; le MAC occupe exactement sa longueur DER, sans bourrage. |
| ISO/TS 32005:2023 | Rôles qualifiés, espaces de noms standards/personnalisés, résolution des correspondances, rôles communs PDF 2.0 et règles d’inclusion du tableau 5 | La matrice source complète est reproductible. Les résolutions publiées se sélectionnent explicitement ; aucune interprétation d’une ambiguïté n’est inventée silencieusement. |
| PDF Declarations | Objets Declaration/ClaimData, dates et schéma d’extension XMP PDF/A facultatif | Une déclaration est une assertion de l’auteur, avec une portée de métadonnées précise ; ce n’est pas un certificat d’audit. |
| WTPDF 1.0.0 | Niveaux explicites d’audit réutilisation/accessibilité ; contrôles de structure, métadonnées, annotations et utilisation des fontes | Le rapport distingue les erreurs détectées des vérifications sémantiques et des programmes de fonte encore à examiner. Aucune certification PDF/UA-2 automatique n’est annoncée. |
| Note d’application 001 | `UseBlackPtComp` avec exactement `ON`, `OFF` ou `Default` | Vérification de version PDF 2.0 et des valeurs, y compris dans les ressources graphiques brutes sans entrée Type. Le périphérique de sortie effectue la gestion des couleurs. |
| Note d’application 002 | Fichiers associés aux objets d’information, contenu marqué, descripteur de contenu chiffré et enveloppe documentaire | Les contrôles du graphe effectif couvrent la découverte des fichiers, les relations, la collection masquée et le document extérieur non chiffré. |
| Note d’application 003 | Flux de métadonnées d’objets, portée des ressources, propriétés nommées de contenu marqué, parties documentaires et DPM | La sérialisation XMP native produit du XML UTF-8 échappé. Le XML et les contenus opaques fournis par l’appelant demandent leur propre validation. |

Le catalogue de base ISO 32000-2 inventorie 440 tableaux et modélise 306 tableaux
de dictionnaires avec 1 709 entrées fixes ou variables. Les pages de continuation
et les corrections d’extraction sont traçables. Cette couverture et les mécanismes
complémentaires n’établissent pas la conformité à toutes les clauses de la norme.
Le [guide PDF 2.0](pdf-2-0.md) et la [couverture](coverage.md)
conservent cette distinction. Le lecteur 0.5 fournit séparément l'authentification
explicite par mot de passe ou [Adobe.PubSec](https://pdftoolkit.github.io/fr/modules/reader/public-key-authentication.html),
le décodage et la vérification du MAC PDF source. Voir son
[guide de mot de passe](https://pdftoolkit.github.io/fr/modules/reader/authentication.html)
et son [guide du MAC source](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html).

## Des algorithmes sélectionnés indépendamment

`ModernStandardSecurityHandler` construit les données d’authentification R=6
AES-CBC ou R=7 AES-GCM à partir des mots de passe utilisateur et propriétaire
explicitement préparés. `ModernFileEncryption` lie ces données, la clé du fichier
et l’opération cryptographique. `Pdf20Permissions` maintient la cohérence entre
les permissions et l’exigence de MAC. Une extension ISO est un élément de tableau
sous `Extensions.ISO_` ; déclarer le niveau 32004 ne déclare pas implicitement
les niveaux 32001, 32002 ou 32003.

`PdfMacTokenComposer` se lie à la clé de chiffrement réellement utilisée et au
`KDFSalt` de 32 octets. Le writer réserve une case hexadécimale exacte, fixe les
plages d’octets, calcule le condensat des octets définitifs et insère le jeton DER
sans déplacer les offsets. L’écriture incrémentale conserve les octets antérieurs
et demande une nouvelle opération MAC pour la nouvelle révision. Ces règles
s’appliquent aussi à la sortie linéarisée.

```php
$mac = new PdfMacTokenComposer($encryption->key, $salt, new SystemRandomSource());
$revision = (new FileWriter(encryption: $encryption, mac: $mac))->revision($file);

$nextMac = new PdfMacTokenComposer($encryption->key, $salt, new SystemRandomSource());
$next = (new IncrementalWriter(mac: $nextMac))->serialize(
    new IncrementalUpdate($revision, $explicitDelta),
);
```

Pour une révision signée, sélectionner `macSignature: $pending` sur le writer
et passer `mac: $mac` à `PreparedSignature`. Le MAC devient un attribut CMS non
signé lié aux plages d’octets du PDF et aux octets réels de la signature du
SignerInfo. Un MAC autonome ne peut pas être conservé tel quel lorsque la
signature modifie les octets réservés. La capacité inclut le MAC attaché ; un
dépassement exige une nouvelle réservation et une nouvelle signature.

L’extension OpenSSL de PHP exécute les primitives RSA/ECDSA prises en charge.
Ed25519 et Ed448 utilisent un exécutable OpenSSL sélectionné explicitement via
le fournisseur dédié, car PHP 8.3 n’expose pas l’opération EdDSA nécessaire. Ce
fournisseur reçoit explicitement l’exécutable et la clé ; choisir les autres
algorithmes ne lance aucun processus. Voir le [tutoriel des signatures et de
l’intégrité](tutorials/31-pdf20-modern-signature.md).

## Vérifier le MAC source avant de lire le contenu protégé

Le lecteur 0.4 utilise `PdfMacTokenVerifier` du core via un
`StandardPasswordAuthentication` choisi explicitement. Il vérifie `AuthCode`
autonome du dernier trailer physique ou son MAC attaché à une signature avant
de retourner le contenu protégé du catalogue. L'étendue lexicale du véritable
jeton et le `ByteRange` direct doivent couvrir tout le fichier courant sauf ce
jeton. Un MAC hérité n'authentifie pas une nouvelle révision ; rechercher des
octets identiques ne prouve pas l'identité du jeton exclu. Les attachements aux
signatures et horodatages documentaires sont pris en charge dans les limites
documentées des jetons hexadécimaux directs.

`SourceIntegrityPolicy::AcceptUnprotected`, valeur compatible par défaut,
vérifie tout MAC signalé mais accepte aussi les PDF non protégés. Choisir
`RequirePdfMac` lorsque l'entrée doit être protégée : un PDF clair ne révèle
pas que tous les marqueurs de chiffrement et d'intégrité ont été supprimés.
`DocumentReader::sourceIntegrityPolicy()` expose l'exigence configurée ;
`requiringSourceIntegrity()` la conserve ou la renforce avec les mêmes
identifiants et limites. Une entrée protégée invalide ne provoque pas de repli
vers un déchiffrement non authentifié.

La vérification utilise la clé Standard R5–R7 authentifiée ou la clé
DefaultCryptFilter PubSec moderne et couvre les octets
chiffrés originaux et la structure du fichier. Elle ne vérifie ni mathématiquement
la signature, ni la confiance envers le certificat ou la TSA. Toute personne
détenant cette clé de fichier peut créer un nouveau MAC. Aucune requête de
ressource externe, certificat ou révocation n'est effectuée. Le
[guide du module](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html)
décrit les budgets CMS/octets, algorithmes pris en charge, quinze fichiers réels
indépendants, cas hostiles et frontières de cadrage exactes. Les anciens MAC
ne sont pas tous revérifiés indépendamment. PubSec utilise la même frontière
d'intégrité source après son authentification destinataire explicite.

## Les métadonnées et déclarations ont un propriétaire

`XmpPacket` compose les propriétés, collections RDF, alternatives linguistiques
et déclarations. `MetadataStream` écrit le flux XML ; `MetadataEntry` le relie
indirectement à son propriétaire PDF. Une déclaration dans les métadonnées du
document porte sur ce document. Sur un objet ou une séquence marquée, sa portée
se limite à cet élément. Les propriétés de métadonnées ne deviennent pas
automatiquement du texte visible sur la page.

Les propriétés nommées du contenu marqué se résolvent dans les ressources de la
page, du Form XObject, du motif de pavage ou de la fonte Type 3 concernés. Les
faits d’émission sont figés avec le flux réellement sérialisé : une modification
non écrite du constructeur ne réinterprète pas une révision antérieure. Les
références directes à un flux de métadonnées dans le contenu sont refusées.

`DocumentPart`, `DocumentPartRoot` et `DocumentPartMetadata` représentent les
parties documentaires et leurs données. Le contrôle du graphe vérifie la
hiérarchie, les plages de pages et les associations réciproques entre pages et
parties. Un contenu chiffré emploie un document extérieur distinct, un fichier
associé de relation `EncryptedPayload`, un descripteur EP et une collection
masquée. Le document extérieur reste lisible sans déchiffrer son PDF intérieur.
Les tutoriels expliquent les [métadonnées et parties](tutorials/28-pdf20-metadata-declarations.md)
et l’[enveloppe chiffrée](tutorials/29-pdf20-encrypted-payload.md).

## Règles de structure et audit WTPDF

`StructureNamespace`, `StructureRole` et `NamespaceRoleMap` font de l’espace de
noms une partie de l’identité du rôle. `NamespaceRoleResolver` suit les
correspondances qualifiées et refuse les cibles introuvables et les cycles.
Le document effectif doit être PDF 2.0 lorsque ces mécanismes sont utilisés, y
compris pour les objets conservés dans une révision incrémentale.

`StructureInclusionRules` applique la matrice source aux rôles réels des parents
et enfants, avec l’exemption PDF 1.7 et les règles de mélange des espaces de noms.
Les corrections 336 et 440 se sélectionnent explicitement. L’occurrence littérale
`c` du document fourni est conservée dans l’inventaire ; la résolution publiée
sélectionnée en fournit l’interprétation.

`WtPdfAudit` produit les observations du niveau de conformité choisi. Le rapport
n’assimile pas « aucune erreur détectée » à « conforme » : l’ordre de lecture
pertinent, les descriptions alternatives appropriées, la fidélité des
correspondances Unicode et les faits relatifs aux programmes de fonte externes
demandent encore des preuves. Le [tutoriel des espaces de noms](tutorials/30-pdf20-tagged-namespaces.md)
présente un rapport concret à côté du PDF balisé réellement généré.

### Comparer explicitement le texte enrichi des champs

Le core 0.8.0 fournit un backend XML natif optionnel pour la clause WTPDF 8.10.3.3
(page physique 46) :

```php
use PDF\Document\Structure\WtPdfGraphChecks;
use PDF\Document\Structure\WtPdfRichTextChecks;
use PDF\Document\Structure\WtPdfXmlRichTextParser;

$checks = new WtPdfGraphChecks(
    richText: new WtPdfRichTextChecks(new WtPdfXmlRichTextParser()),
);
```

Avec `ext-dom`, le parseur décode le contenu paragraph/span et les entités XML
acceptés, normalise les fins de ligne et compare le résultat à la valeur `V`
canonique héritée du champ. L'analyse reste locale au document, bornée, et refuse
DTD, entités externes, ressources distantes et contenu actif. Sans backend, pour
un flux `RV` opaque ou des namespaces/CSS non pris en charge, le contrôle reste
en attente au lieu de réussir. Un parseur plus riche peut être fourni explicitement.
Ce domaine de comparaison mécanique est couvert ; le sens humain et les autres
exigences WTPDF demandent toujours leurs propres preuves.

### Examiner les programmes de glyphes Type 3 réellement utilisés

L'audit natif d'utilisation des fontes sélectionne les `CharProcs` gérés à
partir des véritables codes d'octets affichés. `Type3GlyphSelection` conserve
les glyphes distincts dans l'ordre de première utilisation ; il n'invente ni
conversion Unicode ni glyphe par défaut implicite. Seuls les programmes
sélectionnés et rendus créent des obligations d'incorporation de fontes
auxiliaires. Leurs ressources locales, Forms imbriqués et états graphiques
hérités sont examinés avec les mêmes budgets cumulatifs d'opérations, de texte
et de récursion. Déclarer les ressources d'un glyphe inutilisé ne les rend pas.

ISO 32000-2 §9.3.6 supprime les descriptions de glyphes Type 3 dans les modes
de rendu du texte 3 et 7. L'audit suit cette règle et détecte toujours les codes
affichés indéfinis ou explicitement `.notdef`. Les vérifications indépendantes
qpdf/pypdf/Poppler examinent cinq véritables PDF. Poppler peut exécuter un glyphe
Type 3 en mode 7 ; cette observation est consignée sans être comptée comme
confirmation de la règle de suppression de la norme. Contenu opaque,
dictionnaires Type 3 génériques non gérés, validité du programme de fonte,
licence et sens Unicode demandent encore leurs propres preuves. Le
[registre relié aux sources](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/type3-usage.json)
conserve explicitement ces limites.

### Signaler les fonctionnalités dépréciées dans leur contexte réel

`WtPdfDeprecatedChecks` examine le graphe construit selon les entrées explicites
de `WtPdfDeprecatedCatalogue`, avec clauses sources et pages physiques. Il
distingue domaines de dictionnaires, opérateurs de contenu et contexte de
fichier fourni. Une clé privée sans rapport portant le même nom ne prouve pas
l'utilisation d'une fonctionnalité PDF dépréciée. Les nœuds partagés et arêtes
répétées consomment des budgets explicites ; charges opaques, contexte de trailer
omis et sémantiques non résolues demandent encore une validation complémentaire.

WTPDF §6.2 recommande d'éviter les fonctionnalités dépréciées avec **should**.
Le rapport expose donc des constats `Recommendation` et `recommendations()`
séparément de `failures()` et `pending()`. Une recommandation ne devient pas
silencieusement une erreur bloquante. Les interdictions WTPDF indépendantes
restent des erreurs lorsqu'elles s'appliquent. Fournir
`WtPdfDeprecatedFileContext` pour examiner le contexte de trailer/chiffrement
construit ; il n'authentifie pas des octets importés. CMS, CMaps et formats
embarqués opaques demandent leurs propres parseurs. Une liste d'erreurs vide
ne prouve toujours pas la conformité WTPDF ou PDF/UA.

## Conserver les signatures avec horodatages et données de validation

`PendingDocumentTimestamp` possède un dictionnaire `/DocTimeStamp` avec le
SubFilter `ETSI.RFC3161`. `Rfc3161TimestampBackend` envoie à un fournisseur
explicite l’empreinte réelle du document et un nonce, puis vérifie le jeton reçu,
la liaison à l’autorité et la signature CMS. `LocalTimestampAuthority` est un
fournisseur hors ligne choisi explicitement ; il ne lance aucune requête réseau
et n’établit aucune confiance publique.

`DocumentSecurityStore` contient des flux indirects de certificats, CRL et OCSP.
`ValidationRelatedInformation` exige une politique de validation choisie par
l’appelant qui réussit et identifie les Contents exacts d’une signature antérieure,
bourrage compris. Le graphe refuse un VRI antérieur à sa signature ou des preuves
absentes des tableaux DSS correspondants. Un horodatage ultérieur couvre aussi
les preuves ajoutées.

ISO 32000-2 exclut les horodatages et le DSS de l’évaluation DocMDP.
`DocumentTimestampRevisionPolicy` prouve une révision de maintenance limitée par
comparaison avec tous les objets précédents figés avant de l’autoriser sous P1 :
pages, contenu, widgets et signatures ordinaires ne peuvent pas être modifiés
en même temps. FieldMDP et les verrous de champs supplémentaires restent actifs.
Le [tutoriel d’horodatage](tutorials/32-pdf20-timestamp-dss.md) explique trois
révisions réelles ; l’oracle indépendant vérifie aussi les historiques certifiés,
chiffrés et linéarisés.

## Les mesures géospatiales conservent leur système de coordonnées

`GeographicCoordinateSystem` et `ProjectedCoordinateSystem` identifient un code
EPSG ou une chaîne WKT explicites. `GeospatialControlPoints` apparie les positions
locales et réelles pour construire les tableaux LPTS/GPTS correspondants.
`GeospatialMeasure`, `Viewport` et `Viewports` relient ces mesures à leur véritable
page, Form ou image. `PreferredDisplayUnits`, `ProjectedCoordinateSystemMatrix`
et `PointDataCollection` complètent les préférences d’affichage, le calcul affine
et les objets de nuage de points.

La validation native et celle du graphe effectif contrôlent les contextes, valeurs
finies, dimensions appariées, limites normalisées et exigences de version. Elles
ne consultent pas de registre SIG et ne convertissent pas de projections.
Le [tutoriel géospatial](tutorials/33-pdf20-geospatial.md) explique deux zones
d’exemple déclarées indépendamment et leurs données sérialisées.

## La navigation peut cibler un élément logique

`StructureDestination` désigne un véritable membre de l’arbre de structure et un
`DestinationView` explicite. La résolution de page suit le premier contenu dans
l’ordre déclaré des enfants, avec repli sur la première page si aucun contenu ne
convient. Actions GoTo et dictionnaires de destination nommés conservent leur
repli de page à côté de `SD`. Les formes distantes ou incorporées utilisent des
ID en chaînes d’octets explicites sans ouvrir un autre fichier. Les contrôles du
graphe effectif préservent ces relations dans les révisions conservées.
Le [tutoriel des destinations de structure](tutorials/34-pdf20-structure-destinations.md)
montre les liens sémantiques et leurs véritables objets PDF.

## Vérifications indépendantes

La suite PHP est exécutée sous PHP 8.3, 8.4 et 8.5. Les contrôles complémentaires
emploient des implémentations distinctes :

- pyHanko valide les fichiers AES-CBC et AES-GCM protégés par mot de passe ou
  certificat, leurs MAC autonomes et attachés, les révisions historiques et le
  refus des altérations.
- cryptography et les outils ASN.1 vérifient les signatures courbe/condensat et
  les jetons MAC.
- pyHanko et OpenSSL vérifient les jetons RFC3161, DSS/VRI, certifications et
  chaque préfixe historique signé, au-delà de la seule dernière révision.
- qpdf contrôle les structures écrites et déchiffre indépendamment le contenu
  de l’enveloppe ; pypdf et un analyseur XML inspectent métadonnées et relations.
- La matrice TS 32005 est régénérée à partir de toutes ses pages et comparée à
  la ressource et à la représentation PHP enregistrées.

Ces contrôles établissent les comportements testés. Ils ne promettent pas que
n’importe quelle donnée applicative est sûre ni qu’une déclaration de
conformité fournie par l’auteur est vraie.

## Originaux conservés et provenance

Les onze originaux conservent leurs noms et octets fournis dans le dossier
`resources/reference-documents/` du core.
Le [manifeste des sources](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-bundle/sources.json)
enregistre leurs empreintes, tailles, pages physiques et collections de
corrections. Le site les relie au dépôt sans les ajouter aux installations
Composer ni dupliquer ces fichiers volumineux dans la documentation.

- [ISO 32000-2:2020 EC3, nouvelle copie fournie](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3%281%29.pdf)
- [ISO/TS 32001:2022 EC3](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_TS_32001-2022_sponsored_EC3.pdf)
- [ISO/TS 32002:2022 EC3](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_TS_32002-2022_sponsored_EC3.pdf)
- [ISO/TS 32003:2023](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_TS_32003-2023_sponsored.pdf)
- [ISO/TS 32004:2024](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO-TS-32004-2024_sponsored.pdf)
- [ISO/TS 32005:2023](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO-TS-32005-2023-sponsored.pdf)
- [PDF Declarations](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF-Declarations.pdf)
- [Well-Tagged PDF 1.0](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/Well-Tagged-PDF-WTPDF-1.0.pdf)
- [Note d’application 001 : compensation du point noir](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF20_AN001-BPC.pdf)
- [Note d’application 002 : fichiers associés](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF20_AN002-AF.pdf)
- [Note d’application 003 : emplacements des métadonnées](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF20_AN003-ObjectMetadataLocations.pdf)
