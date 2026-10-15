# 29. Enveloppe lisible et PDF incorporé chiffré

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/pdf20-encrypted-payload.php)
crée deux documents : un PDF protégé par mot de passe et une enveloppe PDF 2.0
non chiffrée qui l'incorpore. La page de l'enveloppe explique comment accéder
au contenu ; la collection identifie le fichier à ouvrir. Le contenu incorporé
est réellement chiffré avant son insertion.

## Exécuter l'exemple

Depuis un checkout du core **0.7.1**, avec PHP 8.3 ou supérieur et OpenSSL :

```bash
php examples/pdf20-encrypted-payload.php wrapper.pdf
```

L’exemple fournit Courier avec des [métriques explicites](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/fixtures/pdf20-courier-font.php) : FirstChar/LastChar, largeurs ASCII et FontDescriptor. PDF 2.0 ne permet plus d’omettre ces entrées pour les quatorze polices standard. Cette construction n’incorpore pas de programme de fonte ; un profil exigeant l’incorporation demande une fonte explicitement incorporée.


Le mot de passe de lecture de démonstration est **`demo-reader`**. Il est écrit
sur la page et dans le code afin que le PDF téléchargé puisse être inspecté.
Il ne convient pas à un document confidentiel. Les clés, sels et vecteurs
d'initialisation sont produits par `SystemRandomSource`.

## Chiffrer le vrai document avant de l'incorporer

`ModernStandardSecurityHandler` construit une opération de chiffrement explicite
avec les mots de passe préparés, les permissions PDF 2.0 et le choix de chiffrer
les métadonnées. L'exemple utilise R=6 avec AES-256-CBC. `FileWriter`, auquel
l'opération est fournie, écrit le dictionnaire de chiffrement et les chaînes
et flux chiffrés du PDF intérieur.

```php
$security = (new ModernStandardSecurityHandler(
    new OpenSslAes256Backend(),
    new SystemRandomSource(),
))->create(
    new PreparedPassword('demo-reader'),
    new PreparedPassword('demo-owner'),
    new Pdf20Permissions(-4),
    new EncryptMetadata(true),
);
$encryptedBytes = (new FileWriter(encryption: $security))->serialize($inner);
```

Les valeurs ASCII de démonstration sont déjà préparées. `PreparedPassword`
représente ce choix explicite ; son constructeur ne normalise pas un mot de
passe arbitraire. Pour les entrées Unicode d'une application, suivre le contrat
de préparation du handler choisi. Le PDF intérieur reçoit également son
identifiant de fichier explicite dans le trailer.

`EmbeddedFileStream` reçoit ensuite **les octets du PDF chiffré**, le type MIME
`application/pdf` et la date source. Le filtre Flate de l'enveloppe compresse ces
octets ; il ne remplace pas leur chiffrement. Ajouter uniquement un nom
`EncryptedPayload` à un flux clair n'assurerait aucune protection.

## Décrire le payload et fermer ses références

La spécification de fichier contient `EF`, `AFRelationship /EncryptedPayload`
et le dictionnaire `EP` :

```php
$descriptor = new EncryptedPayload(new NameType('Standard'));
$specification = new FileSpecification(
    new LiteralString('payload.pdf'),
    $options,
    new AssociatedFileRelationship(AFRelationship::EncryptedPayload),
    encryptedPayload: $descriptor,
);
```

`EP.Subtype /Standard` indique le handler réellement utilisé par le PDF
incorporé. `EP.Version` est un nom de version facultatif, distinct d'un nombre
réel PDF ; aucun n'est ajouté ici. `EncryptedPayload` décrit les moyens d'accès
au fichier. Cet objet n'invente pas son algorithme et ne chiffre pas ses données.

La même spécification indirecte est placée dans `Names.EmbeddedFiles` et dans
le tableau `AF` du catalogue. La clé de l'arbre de noms est `payload.pdf`.
L'enveloppe ne contient qu'un seul fichier dans cet arbre, conformément au
mécanisme d'enveloppe non chiffrée.

## Sélectionner le contenu tout en gardant les instructions lisibles

`Collection(view: CollectionView::Hidden, initialDocument: ...)` écrit
`View /H` et `D (payload.pdf)`. `D` reprend **la clé de l'arbre de noms**,
plutôt qu'un chemin de disque ou une référence arbitraire. Le catalogue lie
explicitement cette collection, les noms et l'association AF.

L'enveloppe elle-même est écrite sans opération de chiffrement. Sa page reste
donc lisible par un processeur qui ne sait pas ouvrir le contenu incorporé.
Un processeur capable peut ouvrir automatiquement le document sélectionné ;
d'autres lecteurs affichent la page d'instructions et leur panneau de pièces
jointes. L'exemple explique aussi l'extraction manuelle.

Le graphe effectif contrôle ces relations lors d'une écriture complète ou
incrémentale : descripteur `EP`, fichier incorporé, unique entrée de noms,
sélection `D`, vue cachée et absence de chiffrement de l'enveloppe. Retirer une
relation nécessaire ou remplacer la collection par une sélection incohérente
fait échouer l'opération.

## Vérifier les deux niveaux indépendamment

L'aperçu ci-dessous rend **l'enveloppe**, pas le contenu déchiffré. Télécharger
le PDF, extraire `payload.pdf`, puis l'ouvrir avec `demo-reader` permet de voir
la page intérieure. Le téléchargement n'exécute aucune pièce jointe.

`tools/validate_pdf20_metadata.py` inspecte l'enveloppe avec pypdf, retrouve
exactement le même fichier dans l'arbre de noms et dans `AF`, extrait ses octets,
vérifie son dictionnaire R=6 et le déchiffre avec qpdf. Il relit ensuite le texte
de la page déchiffrée. Les tests natifs vérifient aussi les enveloppes incohérentes
et les changements incrémentaux ; la réussite du rendu de l'enveloppe ne suffit
pas à démontrer le chiffrement intérieur.

Sources conservées : [ISO 32000-2, pages physiques 109–110](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf#page=109)
pour l'enveloppe et la table 28 ;
[spécification de fichier, pages 149–152](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf#page=149) ;
[note sur les fichiers associés, page 10, §4.1.5](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF20_AN002-AF.pdf#page=10).
Le bundle provient de l'[accès sponsorisé de la PDF Association](https://pdfa.org/sponsored-standards/).

[Parcours des tutoriels](README.md) · [Métadonnées et parties de document](28-pdf20-metadata-declarations.md)
