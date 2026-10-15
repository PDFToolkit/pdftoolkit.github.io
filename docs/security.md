# Revue de sécurité

Cette revue documente les contrôles de sécurité effectués sur le générateur PHP et ses dépendances verrouillées : revue de code, tests de régression, audit des dépendances et validation des PDF par des lecteurs indépendants. Elle couvre la sérialisation des valeurs PDF, les images inline, les ressources binaires, les graphes, les limites numériques et l'écriture des fichiers. Les résultats ci-dessous correspondent aux surfaces et scénarios vérifiés ; ils ne constituent pas une garantie d'absence de toute vulnérabilité.

Les contrôles des convertisseurs TrueType et PNG/JPEG sont maintenant maintenus
dans les modules optionnels [pdf-fonts](https://github.com/PDFToolkit/pdf-fonts)
et [pdf-images](https://github.com/PDFToolkit/pdf-images). Les objets PDF et leurs
invariants restent dans le core. Le module
[pdf-reader](https://github.com/PDFToolkit/pdf-reader) a sa propre
[documentation de sécurité](https://github.com/PDFToolkit/pdf-reader/blob/v0.3.1/docs/security.md)
pour la lecture de fichiers externes ; cette revue du générateur ne s'y substitue pas.

Les versions documentées sont le core **0.8.1**, le lecteur PDF **0.3.1**, les modules images/fontes **0.1.9** et
OpenType indépendant **0.2.0**. Ces packages nécessitent **PHP 8.3 ou supérieur**
et sont vérifiés sous PHP 8.3, 8.4 et 8.5. Le core **0.8** et OpenType **0.2** exigent PHP en
64 bits ; OpenType reste indépendant du core PDF. La revue inclut les
[mécanismes complémentaires PDF 2.0](pdf-2-0-bundle.md) ; les définitions de
source et déclarations de conformité ne sont pas des certificats de sécurité.
Le parseur OpenType indépendant possède ses propres
[frontières de sécurité](https://github.com/PDFToolkit/opentype/blob/v0.2.0/SECURITY.fr.md).

Le module PDF vers HTML **0.3.2**, avec le lecteur **0.3.1+**, conserve ses propres
[contrôles de sécurité](https://pdftoolkit.github.io/fr/modules/to-html/security.html)
et [politiques explicites](https://pdftoolkit.github.io/fr/modules/to-html/policies.html).
Ses tests indépendants vérifient filtrage HTML/CSS/URL, associations et IDs,
budgets cumulatifs, images inline et confinement du runtime aux contrôles liés.
Par défaut, scripts PDF, ressources distantes et actions ResetForm/SubmitForm sont
désactivés. Activer le reset de la bibliothèque n'autorise pas les scripts source.
Le moteur de rendu reste fourni par l'application. L'authentification native par
mot de passe est une sélection explicite du lecteur ; le
[guide HTML d'authentification](https://pdftoolkit.github.io/fr/modules/to-html/authentication.html)
montre sa construction. Le lecteur HTML doit appliquer les permissions vérifiées.
Un mauvais mot de passe natif ne déclenche pas un autre fournisseur.

Le lecteur 0.3.1 limite l'exemption `EncryptMetadata=false` au véritable objet
de métadonnées du catalogue ; les métadonnées de pages et Forms restent chiffrées
sauf sélection explicite d'Identity. Il résout les types indirects avant de
choisir `EFF`, utilise la clé V4 fixe de 128 bits et ignore les tentatives de
redéfinir le filtre standard Identity. Ses [sept régressions supplémentaires](https://github.com/PDFToolkit/pdf-reader/blob/v0.3.1/tools/validate_metadata_security.py)
utilisent qpdf et cryptography, avec les limites précises des oracles expliquées
dans le [guide d'authentification](https://pdftoolkit.github.io/fr/modules/reader/authentication.html).

Le lecteur 0.4.1 conserve les numéros et générations terminaux des chaînes
`Encrypt`, `Root` et `Metadata` du catalogue. Relire les credentials O/U ne les
déchiffre pas ; seule la véritable métadonnée du catalogue, de type correct,
bénéficie de l'exemption implicite de texte clair. Quatre cas d'alias chiffrés
supplémentaires utilisent le parseur strict et le handler Standard inchangés
de pyHanko avec cryptography. Les déchiffreurs de haut niveau qpdf/pypdf/pyHanko
ne suivent pas ces chaînes Encrypt ; leurs anciens contrôles indépendants
restent intacts. Le guide du module précise ces limites d'oracle sans étendre
l'exemption aux métadonnées de pages ou d'objets.

## Mécanismes bornés et capacités explicites

- Les règles de dictionnaire du core exécutent des domaines et relations reliés
  aux sources ; elles n'assainissent pas un graphe arbitraire et ne certifient pas
  toutes les conditions normatives.
- La [caviardisation](tutorials/36-applied-redaction.md) native supprime contenu
  touché, données partagées et canaux annexes avant d'écrire un nouveau fichier.
  La préservation par défaut exige des échantillons device normalisés et une
  sémantique de ressource fiable ; le contenu non pris en charge est refusé et
  les ressources complexes conservées exigent un assainisseur explicite.
  L'opération permet volontairement une suppression excessive.
  Les dépendances inverses Mask/SMask/Form sont exclues globalement ; les
  métadonnées descriptives des fontes disparaissent et les valeurs conservées
  exigent des types et contextes vérifiés. Les bornes après rotation/cisaillement
  utilisent les quatre coins, et les tracés non peints qui traversent une région
  sont supprimés comme géométries récupérables.
- Le parseur XML WTPDF optionnel interdit DTD, entités externes, ressources
  distantes et contenu actif, avec budgets d'octets/nœuds/profondeur. Le texte
  enrichi non pris en charge reste en attente ; comparer le XML ne prouve pas l'accessibilité.
- Le lecteur 0.3 authentifie des credentials R=2–7 explicites et déchiffre chaque
  payload une seule fois. Filtres nommés, flux d'objets et tags AES-GCM disposent
  de fixtures indépendantes. Le texte déchiffré partage les budgets cumulatifs ;
  le ciphertext original reste accessible séparément. Le lecteur 0.4 vérifie
  aussi tout MAC PDF source signalé avant d'interpréter le contenu protégé.
  `RequirePdfMac` refuse une entrée non protégée ou privée de ses marqueurs ;
  la valeur compatible par défaut accepte aussi les PDF ordinaires non protégés.
  Identité lexicale du jeton, couverture de tout le fichier courant et cadrage
  CMS sont contrôlés. Cela ne vérifie ni mathématiquement la signature ni la
  confiance du certificat ; qui détient la clé du fichier peut créer un nouveau
  MAC. Le [guide du MAC source](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html)
  explique politiques, budgets et frontières de refus. L'authentification par
  clé publique en entrée reste indisponible.
- La préparation des codes-barres compresse la valeur explicite entière avant
  sa répartition ordonnée et vérifie les budgets cumulatifs avant l'appel
  suivant de l'encodeur fourni. Le core construit les images natives `AP.N`
  sur tout le rectangle ; symbologie, zones de silence et exécution propre
  de l'encodeur restent sa capacité explicite.
- L'inspection WTPDF des Type 3 suit les véritables programmes de glyphes
  sélectionnés et leurs ressources imbriquées bornées. Les contrôles contextuels
  de dépréciation distinguent recommandations et erreurs ; programmes opaques
  et contexte de fichier absent restent en attente.
- OpenType 0.2 borne les lookups contextuels, l'expansion des glyphes et les
  tables de variation. Substitution et positionnement natifs sont comparés à
  HarfBuzz ; ils n'exécutent pas le hinting et ne forment pas un shaper Unicode complet.

## Résultats et protections

| Surface | Résultat de la revue |
| --- | --- |
| Noms, chaînes, nombres, header | Échappement des séparateurs et des octets, chaînes littérales préservant les données, nombres finis et version de header limitée par enum. Les charges essayant de fermer une chaîne ou d'introduire d'autres objets restent des données. |
| Flux PDF | `/Length` calculée sur les octets encodés. Les marqueurs `endstream` présents dans les données ne modifient pas cette longueur. Les entrées externes `/F`, `/FFilter` et `/FDecodeParms` sont refusées par `StreamObject`. |
| Images inline | Correction d'une ambiguïté `EI` : un lecteur tolérant peut reconnaître le terminateur sans blanc avant lui. Les octets pourraient alors être lus comme opérateurs de contenu. Ces séquences sont désormais refusées ; un XObject image fournit une représentation séparée avec longueur explicite. |
| Dimensions d'image | Calcul entier contrôlé des octets par ligne et du total. Un débordement est refusé au lieu de passer par un flottant puis une longueur incorrecte. |
| Import PNG/JPEG — module pdf-images | Octets fournis explicitement, sans chargement de chemin/URL. Limites sur les octets, pixels, dimensions et segments ; PNG CRC/ordre/filtres/zlib borné ; JPEG marqueurs, tables et couleurs inspectés. Les coefficients JPEG sont décodés par le lecteur PDF. |
| Programme TrueType — module pdf-fonts | Validation des données binaires fournies explicitement : tables, offsets, métriques, cmap et glyphes contrôlés ; cycles et profondeur des glyphes composés bornés. CFF, fontes variables et collections non prises en charge sont refusées. |
| Opérandes partagés | La validation visite chaque identité une seule fois, avec un ensemble distinct pour les ancêtres actifs. Elle conserve le refus des cycles sans revisiter exponentiellement un sous-graphe partagé. |
| Références croisées | Les trous initiaux reçoivent des enregistrements libres conformément à la norme. La capacité cumulée est bornée avant leur allocation par `CrossReferenceLimits`. Les sections incrémentales restent partielles ; les additions pour `/Size` et le numéro du flux xref sont contrôlées. |
| Révisions | Réservations des anciens numéros, conservation des générations et des alias ; remplacement de conteneurs structuraux refusé même à travers un nouveau flux d'objets. Les métadonnées du catalogue et de l'arbre de pages sont contrôlées sur les valeurs effectives. Les anciens octets demeurent dans le fichier : une update ne permet pas d'effacer un secret. |
| Sortie fichier | Validation du chemin avant sérialisation, refus des URI de streams, exception d'écriture sans divulgation du chemin. Une erreur de validation du graphe intervient avant l'ouverture de la destination existante. |
| Dépendances | Aucun avis connu ni paquet abandonné signalé par `composer audit --locked` lors de la revue. Ce contrôle est exécuté à chaque CI. |
| Chiffrement historique Adobe R=5 | Vecteurs AES officiels, fixtures qpdf et déchiffrement indépendant des chaînes et flux, avec mots de passe utilisateur/propriétaire et rejets des mauvais mots de passe. Vérification des longueurs après filtres et chiffrement, de l'absence de double chiffrement et des exceptions structurelles. |
| Préparation des mots de passe | SASLprep/NFKC Unicode 3.2 figé, comparé à un oracle indépendant : mappings, caractères interdits et non assignés, règles bidirectionnelles et troncation après normalisation. |
| Chiffrement ISO R=2/3/4 | Algorithmes 1–7, credentials utilisateur/propriétaire, RC4 et AESV2, clés de 40 à 128 bits, filtres implicites et explicites et révisions incrémentales. Les filtres Crypt explicites utilisent leur clé directement selon 7.4.10 ; les flux implicites utilisent la dérivation par objet. |
| Chiffrement par certificats | Messages CMS, regroupement des destinataires, formats s3/s4/s5 et clés distinctes pour le document et les pièces jointes. Vérification indépendante des données CMS, des clés et du déchiffrement. L'ordre des octets des permissions est un choix explicite. |
| Frontière du writer chiffré | Chaînes directes du trailer hors ID refusées ; dictionnaire Encrypt et xref conservés en clair. Seule la métadonnée du catalogue peut être exemptée ; son remplacement suit la liaison effective de la révision. Une nouvelle identité PHP ne permet pas de remplacer Encrypt dans un flux d'objets. |
| Signatures | ByteRange fixé avant signature, réservation Contents à capacité explicite, contrôle des délimiteurs et remplissage sans déplacement des offsets. Les trois formats ISO sont contrôlés par une vérification indépendante des condensats, des messages CMS et des signatures RSA. |

Le rejet explicite des stream URIs est un durcissement du contrat de `writeTo()`, pas la correction d'une exécution PHP démontrée : `LOCK_EX` bloquait déjà les wrappers usuels sur le PHP 8.5 vérifié. Une destination native peut encore suivre un lien symbolique ou désigner un partage réseau selon le système. L'application doit contrôler son emplacement et ses permissions.

## Utiliser les données au bon endroit

`ShowText(new LiteralString($text))` échappe la syntaxe de la chaîne. `NameType($name)` échappe celle du nom. En revanche, `StreamObject($rawContent)` écrit les octets fournis : s'ils sont utilisés comme `/Contents`, ils constituent du code de dessin PDF. Utiliser `ContentStreams` et ses opérateurs typés pour composer un contenu à partir de texte extérieur.

Un PDF peut représenter une action JavaScript, une action de lancement ou une URI. La bibliothèque ne les exécute pas côté PHP et conserve ces définitions parce qu'elles appartiennent au format. Un lecteur peut ensuite les interpréter. Une application recevant des choix d'utilisateurs doit autoriser les types d'actions et les destinations, plutôt que d'accepter librement un graphe ou des entrées arbitraires.

`EncodedData` transmet des octets déjà encodés. Il n'analyse ni ne décompresse un fichier PNG, JPEG ou PDF entrant. Les `PngImageDecoder` et `JpegImageReader` du module `pdftoolkit/pdf-images` effectuent leurs validations dédiées et reçoivent des limites explicites ; ils ne remplacent pas les quotas ni les contrôles d'accès d'un service d'upload. Le `DCTImage` du core accepte une représentation DCT déclarée explicitement sans inspecter ses marqueurs. Les programmes de police sont également des données binaires ; leur analyse appartient à `pdftoolkit/pdf-fonts`. Les moteurs de hinting et le décodage DCT restent exécutés par le lecteur qui ouvre le document.

## Écrire ou servir un document

Le chemin de `writeTo()` doit être choisi par l'application, dans un emplacement maîtrisé. La méthode écrase une destination existante et ne crée pas son répertoire parent. Elle ne constitue ni un bac à sable de chemins, ni une écriture atomique : une erreur matérielle pendant l'écriture peut laisser un fichier incomplet.

Pour une réponse HTTP, l'application peut envoyer les octets de `toPdf()` avec ses propres contrôles d'accès et des en-têtes adaptés :

```php
$bytes = $document->toPdf();
header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="document.pdf"');
header('X-Content-Type-Options: nosniff');
echo $bytes;
```

Le nom de téléchargement est ici fixe. Des données de requête ne doivent pas être interpolées directement dans les en-têtes ou les chemins. Les exemples du dépôt sont des scripts CLI ; leur premier argument est un chemin choisi par la personne qui lance la commande.

## Disponibilité et couverture

Les contrôles numériques évitent les débordements identifiés ; la validation des opérandes évite les revisites inutiles. Ils ne remplacent pas les quotas du service. Un graphe direct partagé peut représenter une très grande sortie lorsqu'il est développé en syntaxe PDF. Une chaîne de filtres peut aussi augmenter fortement le nombre d'octets. Une limite sur la taille des données d'entrée seule ne borne donc pas toute la sérialisation.

Les tests [SecuritySerializationTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/SecuritySerializationTest.php), [SecurityLimitsTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/SecurityLimitsTest.php) et [FileOutputTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/FileOutputTest.php) couvrent les charges d'injection, les 256 valeurs d'octet, les terminateurs inline, les bornes numériques, les graphes partagés et les sorties. [ImageObjectsTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/ImageObjectsTest.php), [CrossReferenceSectionTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/CrossReferenceSectionTest.php) et [IncrementalUpdateTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/IncrementalUpdateTest.php) couvrent les invariants PDF du core. Les régressions de décodage des images sont dans [ImageImportTest du module](https://github.com/PDFToolkit/pdf-images/blob/v0.1.9/tests/ImageImportTest.php). Les validations TrueType restent dans [les tests du module de fontes](https://github.com/PDFToolkit/pdf-fonts/tree/v0.1.9/tests). Des lectures indépendantes avec pypdf ont confirmé les vecteurs binaires et la reproduction de l'ambiguïté inline. qpdf contrôle tous les exemples en CI.

Cette revue n'est pas un audit des lecteurs PDF, de PHP, du serveur HTTP ou d'une future bibliothèque de mise en page. Les fichiers de définition générés expriment les contraintes de la norme ; ils ne forment pas une politique générale d'assainissement des documents.

La revue croisée des nouveaux mécanismes a identifié deux défauts dans les versions
de développement : une exemption de métadonnées attachée à une ancienne identité
et un remplacement de Encrypt par un membre de flux d'objets. Les tests
[EncryptedRevisionInvariantTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/EncryptedRevisionInvariantTest.php)
vérifient leurs corrections, y compris le contenu XML effectivement écrit.

Les validateurs [ISO](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_iso_security.py),
[certificats](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_public_key_security.py) et
[signatures](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_pdf_signatures.py) sont des dépendances de
développement, avec versions et empreintes verrouillées. Chaque oracle précise
les limites de son lecteur : qpdf 12.4.2 dérive aussi une clé par objet pour un
Crypt explicite ; pyHanko vérifie la règle ISO sans modifier ses algorithmes.
Pour certains anciens RC4, pypdf utilise son propre fournisseur général afin
d'accepter toutes les longueurs entières autorisées.

Une signature mathématique ne prouve pas la confiance dans le signataire.
La politique de certificats, la révocation, l'horodatage et l'interprétation des
modifications autorisées demandent des contrôles distincts. Les clés privées
dans les fixtures sont publiques et exclusivement destinées aux tests.

Le backend natif contrôle les algorithmes et les tailles de clés de la table 257
sur la version PDF effective. Le backend CMS historique utilise SHA-256 ;
`ModernCmsSignatureBackend` fournit sa propre sélection explicite de
condensat/courbe et des opérations PDF 2.0 vérifiées indépendamment. L'orchestration
`SignatureFieldSigning` applique les seeds, verrous, certificats et apparences
réellement écrits, puis vérifie mathématiquement le résultat avant de remplir
la réservation. Une exigence de digest ou de preuve indisponible reste refusée.
La signature simple refuse les politiques qui demandent ce contrat dédié.
Une chaîne de certificats déclarée pour une signature PKCS#1 doit commencer par
le certificat effectivement utilisé par ce backend.

Les tests de [vérification des résultats](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/SignatureOutputVerificationTest.php),
de [politique de champ](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/SignatureFieldPolicySigningTest.php) et de
[permissions historiques](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/SignaturePermissionHistoryTest.php) couvrent
les sorties altérées, les certificats divergents, les faits rejoués, les verrous
et les permissions. L'[oracle de politiques](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_signature_field_policies.py)
vérifie huit PDF et neuf signatures RSA/DSA sans modifier les lecteurs.
La comparaison générale des modifications autorisées par MDP/UR demeure distincte.

Le core **0.8.1** applique aussi les restrictions historiques DocMDP/FieldMDP à la
frontière commune du writer incrémental, même sans `PreparedSignature`. Il compare
toutes les différences des révisions figées, pas seulement le champ sélectionné.
Les opérations protégées prises en charge sont la signature terminale et la
maintenance DSS/horodatage documentaire PDF 2.0. Les verrous historiques restent
applicables ; P2/P3 n’autorisent ni remplissage général, ni modification
d’annotations, ni changements étrangers non classifiés. Les mises à jour UR sont
refusées. Les entrées `/Lock` et `/Reference` existantes peuvent rester inchangées
dans une opération autorisée.

Utiliser la `FileRevision` native originale émise dans l’exécution courante. Les
snapshots fournis, clones et sérialisations PHP ne conservent pas cette autorité.
Les signatures historiques terminées exigent une vérification réelle liée aux
octets finaux, `ByteRange`, `Contents`, dictionnaire et certificat du signataire,
y compris au CMS/MAC final le cas échéant. Des octets opaques remis à `finalize()`
ne constituent pas cette preuve. Les contrôles établissent l’intégrité
mathématique, pas la confiance PKI ni une classification générale des changements
de PDF externes. Les [régressions des permissions incrémentales](https://github.com/PDFToolkit/pdf/blob/v0.8.1/tests/IncrementalSignaturePermissionsTest.php)
et l’[oracle indépendant](https://github.com/PDFToolkit/pdf/blob/v0.8.1/tools/validate_incremental_permissions.py)
exercent les opérations natives permises et les changements étrangers refusés.
Le [guide des sources conservées](https://github.com/PDFToolkit/pdf/blob/v0.8.1/resources/signature-revisions/README.fr.md)
consigne les pages exactes, les opérations prises en charge et les choix de migration.

Les tests [AdobeEncryptionTest](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tests/AdobeEncryptionTest.php) et le validateur
[validate_adobe_encryption.py](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_adobe_encryption.py) couvrent le
protocole historique R=5. Ce protocole est sélectionné explicitement pour
l'interopérabilité : sa dérivation de mot de passe est ancienne et AES-CBC
n'authentifie pas le contenu. La préparation SASLprep ne renforce pas un mot de
passe faible. Le [guide Adobe](adobe-supplement.md) précise les mécanismes
effectivement disponibles et leurs limites.

## Frontières de la cryptographie, des métadonnées et de l’audit PDF 2.0

`ModernStandardSecurityHandler` distingue AES-CBC R=6 d’AES-GCM R=7 de TS 32003.
Le second authentifie les valeurs chiffrées et emploie une séquence de nonces
explicite par clé, avec refus des doublons et limite d’invocations. L’application
doit préserver cette allocation pour toute la durée d’utilisation de la clé,
y compris entre processus. PDF MAC de TS 32004 authentifie la révision sérialisée couverte,
y compris ses octets structurels. Les writers natifs calculent un nouveau MAC
autonome ou attaché à la signature pour les sorties initiales, incrémentales et
linéarisées. Chiffrement altéré, mauvais mots de passe, données MAC modifiées
et incohérences clé/sel/permissions sont des cas de régression. AES-CBC seul
n’authentifie pas le contenu et Adobe R=5 historique est refusé en PDF 2.0 effectif.

SHA3-256/384/512, SHAKE256 à sortie fixe et les combinaisons courbe/condensat
modernes prises en charge sont des choix explicites avec déclarations d’extension
ISO séparées. RSA/ECDSA utilise PHP OpenSSL. Ed25519/Ed448 demande un fournisseur
exécutable choisi explicitement, avec clé et exécutable explicites ; les autres
opérations ne lancent pas de processus. Les certificats et clés privées des tests
sont des fixtures publiques, pas des credentials de production. Les contrôles
indépendants pyHanko, cryptography, ASN.1 et OpenSSL valident la sortie réelle ;
voir [l’oracle cryptographique](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_iso32000_crypto.py).

Les horodatages documentaires RFC 3161 exigent un fournisseur de jeton et un
vérificateur d’autorité choisis par l’appelant. Les objets DSS/VRI stockent les
preuves certificat, CRL et OCSP fournies ; leur stockage seul ne prouve ni leur
fraîcheur, ni la révocation, ni la confiance. La politique de maintenance compare
le delta incrémental figé avant d’autoriser l’exception DocMDP restreinte pour
horodatage/DSS. Elle n’autorise pas les changements arbitraires de pages/contenus,
ne contourne pas FieldMDP et ne remplace pas l’analyse générale authentifiée des
révisions. Récupération réseau, racines de confiance et politique de validation
restent des décisions explicites de l’application ; aucune URL de métadonnée
ne déclenche de chargement. Le [tutoriel horodatage/DSS](tutorials/32-pdf20-timestamp-dss.md)
montre les révisions réelles et la frontière de validation des preuves.

Les objets XMP natifs valident les caractères UTF-8/XML et échappent les valeurs
RDF/XML. Propriétaires des métadonnées, ressources du contenu marqué, fichiers
associés, plages de pages DPart et découverte des enveloppes chiffrées sont
contrôlés contre le graphe effectif. Le XML/contenu opaque et les octets de payload
fournis par l’appelant ne sont ni analysés ni approuvés par ce modèle. Une
déclaration exprime l’affirmation de l’auteur à la portée choisie ; elle ne la
prouve pas. L’[oracle des métadonnées](https://github.com/PDFToolkit/pdf/blob/v0.8.0/tools/validate_pdf20_metadata.py)
utilise des lecteurs XML/PDF indépendants et déchiffre séparément le PDF interne
de l’exemple.

`WtPdfAudit` est un **audit mécanique partiel, sans certification**. Références
invalides, rôles non résolus et structures incorrectes deviennent des constats
d’échec ; les booléens indirects valides sont résolus. Les parcours refusent les
cycles et des budgets explicites bornent l’inspection de structure/polices, les
correspondances Unicode cumulées, les opérations et les octets de texte. Dépasser
un budget interrompt l’audit au lieu de produire un rapport réussi. L’absence
d’échec détecté ne dispense pas des vérifications encore nécessaires sur l’ordre
de lecture, l’utilité des descriptions, le sens Unicode ou les programmes de
fonte externes. Le [tutoriel des namespaces](tutorials/30-pdf20-tagged-namespaces.md)
montre les échecs et les preuves restant à fournir.

[Politique et signalements privés](https://github.com/PDFToolkit/pdf/blob/v0.8.0/SECURITY.md) · [Architecture](architecture.md) · [Couverture de la norme](specification.md)
