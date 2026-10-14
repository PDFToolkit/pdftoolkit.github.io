# 31. PDF 2.0 : signatures modernes et intégrité

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-modern-signature.php) produit une page PDF 2.0 lisible et une véritable signature CMS utilisant P-256 et SHA3-256. La page explique les algorithmes choisis. Son champ de signature ne possède pas de widget : le texte visible décrit l’opération, tandis que la signature cryptographique couvre les octets réels du fichier.

Le certificat et la clé privée sont des **données publiques de test**, conservées pour rendre les exemples reproductibles. Leur signature démontre l’opération mathématique sans établir une identité de confiance. L’application fournit explicitement ses propres données d’identité et sa politique de confiance.

## Exécuter l’exemple

Depuis une copie du core 0.7.0 avec ses dépendances de développement verrouillées, sous PHP 8.3 ou ultérieur en 64 bits :

```bash
php examples/pdf20-modern-signature.php modern-signature.pdf
```

L’exemple fournit Courier avec des [métriques explicites](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/fixtures/pdf20-courier-font.php) : FirstChar/LastChar, largeurs ASCII et FontDescriptor. PDF 2.0 ne permet plus d’omettre ces entrées pour les quatorze polices standard. Cette construction n’incorpore pas de programme de fonte ; un profil exigeant l’incorporation demande une fonte explicitement incorporée.


Cet exemple utilise l’extension OpenSSL de PHP pour ECDSA. Ed25519 et Ed448 utilisent un fournisseur distinct dont l’exécutable est choisi explicitement ; charger la bibliothèque ne démarre aucun processus. Le PDF reste non chiffré pour permettre son aperçu dans le navigateur.

## Choisir l’identité et le condensat

`X509Certificate` reçoit les octets DER du certificat. `CertificateChain` et `OpenSslIdentity` associent ce certificat à la clé privée fournie. Aucun chemin, aucune URL de certificat distant ni aucun magasin de confiance du système ne sont déduits.

```php
$identity = new OpenSslIdentity(new CertificateChain($certificate), $privateKeyPem);
$backend = new ModernCmsSignatureBackend(
    $identity,
    SignatureDigestMethod::SHA3_256,
);
```

Le fournisseur lit la courbe nommée dans le certificat réel et contrôle le couple courbe/condensat. P-256 avec SHA3-256 est pris en charge ; P-256 avec SHA-512 est refusé. ECDSA utilise le condensat choisi pour le document et pour les attributs signés CMS encodés en DER. EdDSA possède ses propres règles d’algorithme. Un nom d’algorithme ne suffit pas à contourner ces contraintes.

## Déclarer les extensions indépendamment

```php
$extensions = new IsoExtensions(
    IsoTechnicalSpecification::HashAlgorithms,
    IsoTechnicalSpecification::DigitalSignatures,
);
```

Ces objets écrivent des dictionnaires d’extension distincts dans `Extensions.ISO_`. ISO/TS 32001 apporte les condensats supplémentaires ; ISO/TS 32002 apporte les algorithmes de signature et leurs combinaisons. Choisir le numéro d’extension le plus élevé ne déclare pas le plus petit. Le fichier utilise aussi explicitement `new FileHeader('2.0')`.

SHA3-256, SHA3-384, SHA3-512 et SHAKE256 avec une sortie fixe de 64 octets sont représentés par `SignatureDigestMethod`. EC3 supprime le paragraphe 5.1.3 d’ISO/TS 32001 : l’implémentation n’étend donc pas cette règle supprimée concernant les références de signature.

## Réserver, préparer et signer les octets exacts

`PendingSignature` possède `/Contents`, `/ByteRange`, `/Type`, `/Filter` et `/SubFilter`. Sa `SignatureCapacity(4096)` réserve 4 096 octets de signature, encodés en chaîne hexadécimale dans le PDF. `SignatureField` relie ce dictionnaire exact à l’AcroForm.

```php
$prepared = (new SignatureWriter())->prepare($file, $pending);
$signed = $prepared->sign($backend);
$signed->writeTo($path);
```

La préparation fige les identités des objets, les positions et les plages couvrant le fichier entier. La signature calcule le condensat de ces octets, construit le conteneur CMS et remplit uniquement la région réservée. La longueur du fichier et les positions des objets restent identiques. Si le résultat dépasse la capacité, il faut préparer un autre document avec une réservation plus grande et signer ses nouveaux octets ; aucune troncature n’est utilisée.

Une signature ultérieure demande une nouvelle révision incrémentale. Le préfixe d’octets précédent et les politiques de signature historiques restent dans l’historique figé. La confiance dans les certificats, l’expiration, la révocation et le choix d’algorithmes adaptés au déploiement relèvent de la politique de validation de l’application.

## Ajouter explicitement le chiffrement et PDF MAC

Le chiffrement, les signatures d’approbation et PDF MAC répondent à des besoins différents. `ModernStandardSecurityHandler` choisit R=6 AES-CBC ou R=7 AES-GCM. AES-GCM authentifie chaque valeur chiffrée. ISO/TS 32004 ajoute un MAC couvrant toute la révision sérialisée, y compris ses octets structurels.

Pour une révision chiffrée avec un MAC attaché à la signature :

```php
$writer = new FileWriter(
    encryption: $encryption,
    mac: $mac,
    macSignature: $pending,
);
$prepared = new PreparedSignature($writer->revision($file), $pending, mac: $mac);
$signed = $prepared->sign($backend);
```

`PdfMacTokenComposer` reçoit la clé de chiffrement réelle, le sel KDF de 32 octets et une source aléatoire explicite. Les déclarations d’extension ISO correspondantes et le bit d’autorisation de chiffrement sont exigés. Le MAC est attaché comme attribut CMS non signé et lie à la fois les octets PDF couverts et les octets de signature réels du SignerInfo. Un MAC autonome utilise un emplacement distinct dans le trailer. Chaque révision incrémentale demande un nouveau MAC ; un ancien jeton ne peut pas authentifier des octets ajoutés.

Le [guide du bundle](../pdf-2-0-bundle.md) explique ces constructeurs et leurs frontières. L’aperçu ci-dessous présente l’exemple de signature non chiffré : il ne demande donc pas de mot de passe et ne prétend pas démontrer le chiffrement.

## Vérifier avec des implémentations indépendantes

`tools/validate_iso32000_crypto.py` produit des fixtures chiffrées et protégées par MAC avec les writers natifs. Il utilise pyHanko pour les déchiffrer et les valider, OpenSSL et Python cryptography pour vérifier les signatures CMS, ainsi que qpdf pour les combinaisons structurelles prises en charge. Il exerce les références croisées classiques, en flux et hybrides, les révisions initiales et incrémentales, la linéarisation et des altérations volontaires.

```bash
python tools/validate_iso32000_crypto.py \
  --php php --qpdf qpdf --openssl /usr/bin/openssl \
  --work-dir /tmp/pdf20-crypto
```

Installez les dépendances de validation verrouillées par le dépôt avant d’exécuter cette commande de développement. Elles ne font pas partie des dépendances Composer de production. Les tests vérifient indépendamment les octets émis ; leur réussite ne rend pas le certificat public de démonstration digne de confiance et ne certifie pas tous les profils PDF.

## Références

Les originaux conservés d’[ISO/TS 32001 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32001-2022_sponsored_EC3.pdf), [ISO/TS 32002 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32002-2022_sponsored_EC3.pdf), [ISO/TS 32003](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32003-2023_sponsored.pdf) et [ISO/TS 32004](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO-TS-32004-2024_sponsored.pdf) proviennent de la [PDF Association](https://www.pdfa.org/sponsored-standards/). Le [catalogue du bundle](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/sources.json) consigne les identités des sources, les pages physiques et les annotations de correction.

[Parcours des tutoriels](README.md) · [Guide du bundle](../pdf-2-0-bundle.md) · [Sécurité](../security.md)
