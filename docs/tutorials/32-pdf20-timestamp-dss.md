# 32. Horodatages de document et preuves de validation

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-timestamp-dss.php) écrit un PDF lisible contenant deux véritables horodatages RFC3161. Entre eux, il ajoute des certificats dans un Document Security Store (DSS) et des Validation Related Information (VRI) propres à la signature. La page visible énumère ces étapes ; les preuves se trouvent dans les objets PDF et les plages d’octets historiques signées.

L’autorité de démonstration fonctionne hors ligne avec une **clé publique de test**. Ses signatures mathématiques sont réelles, mais son identité et son horloge locale ne constituent pas un service d’horodatage de confiance. L’application choisit explicitement son fournisseur et sa politique concernant les certificats, le temps et la révocation.

## Exécuter l’exemple

Depuis une copie du core 0.7.0 avec ses dépendances de développement verrouillées, fournissez explicitement l’exécutable OpenSSL :

```bash
php examples/pdf20-timestamp-dss.php timestamps.pdf /usr/bin/openssl
```

L’exemple fournit Courier avec des [métriques explicites](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/fixtures/pdf20-courier-font.php) : FirstChar/LastChar, largeurs ASCII et FontDescriptor. PDF 2.0 ne permet plus d’omettre ces entrées pour les quatorze polices standard. Cette construction n’incorpore pas de programme de fonte ; un profil exigeant l’incorporation demande une fonte explicitement incorporée.


Sous Windows, placez entre guillemets un chemin contenant des espaces. L’exemple accepte aussi `PDFTOOLKIT_OPENSSL` à la place du second argument. Il ne télécharge aucun certificat, clé privée, réponse de révocation ou horodatage sur le réseau.

## Préparer le premier horodatage de document

`PendingDocumentTimestamp` est distinct de `PendingSignature`. Il possède `/Type /DocTimeStamp`, `/SubFilter /ETSI.RFC3161`, `/ByteRange` et la réservation `/Contents`. Son identité indirecte exacte est reliée à un `SignatureField` de l’AcroForm.

```php
$pending = new PendingDocumentTimestamp(new SignatureCapacity(8192));
$field = new SignatureField(
    new PartialFieldName(new TextString('FirstTimestamp')),
    value: new IndirectReference($pending),
);
```

`SignatureWriter` prépare la plage couvrant tout le fichier. `Rfc3161TimestampBackend` calcule le condensat de ces octets et construit une `TimestampRequest` contenant l’empreinte et un nonce. Le fournisseur reçoit cette requête plutôt que le PDF entier. Avant d’insérer le jeton reçu, le backend vérifie l’empreinte, le nonce, la politique lorsqu’elle est demandée, la signature CMS et la liaison au certificat de l’autorité choisie. Le certificat doit posséder l’usage de clé étendu d’horodatage.

`LocalTimestampAuthority` reçoit explicitement l’exécutable, la chaîne de certificats, la clé privée, la source de numéros de série et l’OID de politique. Une intégration de production peut implémenter `TimestampTokenProvider` sans changer le dictionnaire PDF ni le mécanisme de plages d’octets.

## Ajouter les données de validation dans une autre révision

Le premier horodatage signe le fichier initial. Son VRI doit donc être ajouté dans une révision incrémentale ultérieure, après une décision de validation réussie :

```php
$information = new ValidationRelatedInformation(
    $first,
    $policy,
    certificates: $references,
);
$store = new DocumentSecurityStore(
    certificates: $references,
    validation: $information,
);
```

`SignatureValidationEvidence` constitue la frontière explicite de politique de l’application. La politique d’exemple vérifie mathématiquement la fixture publique. En production, elle doit aussi établir les faits requis concernant la confiance dans les certificats, leur validité temporelle et leur révocation. Incorporer un certificat n’établit pas ces faits.

`ValidationDataStream` conserve les octets DER fournis ; `ValidationDataReferences` associe les preuves indirectes à leur nature. DSS accepte des tableaux de certificats, CRL et OCSP. VRI référence les preuves correspondantes déjà présentes dans ces tableaux DSS. Sa clé est le SHA-1 en majuscules des `/Contents` réels de la signature antérieure, **bourrage réservé compris**. Ce n’est pas le condensat du jeton CMS sans bourrage ni celui du document entier.

Le writer examine les véritables octets historiques figés et refuse un VRI sans signature antérieure complète correspondante. Il refuse aussi les natures de preuve incompatibles et les références VRI absentes du stockage documentaire. La modification du catalogue est préparée explicitement avec `IndirectObject` et l’identifiant existant du catalogue ; les anciens octets restent intacts.

## Sceller les preuves ajoutées

Le script ajoute un second champ d’horodatage à l’AcroForm effectif, puis prépare et signe une troisième révision. Cet horodatage couvre le document précédent, le premier horodatage et l’ajout DSS/VRI. Le premier horodatage valide toujours son préfixe d’origine ; il ne couvre pas rétroactivement les preuves ajoutées.

ISO 32000-2 permet d’ignorer les horodatages et le DSS lors de l’évaluation des restrictions DocMDP. L’exception native P1 exige une comparaison stricte de la révision de maintenance : elle ne peut pas masquer des modifications de page, de contenu, de widget ou de signature ordinaire. Les restrictions FieldMDP et les verrous de champs supplémentaires restent actifs. Le validateur indépendant exerce séparément des historiques certifiés P1 ; l’exemple visible se concentre sur les trois étapes de conservation des preuves.

## Vérifier indépendamment les octets historiques

`tools/validate_pdf20_timestamps.py` valide chaque préfixe historique signé avec pyHanko et OpenSSL. Il examine les empreintes RFC3161 réelles, signatures CMS, identifiants de certificat ESS, clés VRI et références de preuves. La matrice comprend les références croisées classiques, en flux et hybrides, la linéarisation, les fichiers clairs/R=6/R=7, PDF MAC et les historiques certifiés.

```bash
python tools/validate_pdf20_timestamps.py \
  --php php --qpdf qpdf --openssl /usr/bin/openssl \
  --work-dir /tmp/pdf20-timestamps
```

Les dépendances de validation verrouillées appartiennent aux outils de développement. Aucune ne devient une dépendance Composer de production. Contrôler uniquement la syntaxe du fichier ou sa dernière signature ne vérifierait pas tout l’historique ni la politique de confiance de l’application.

## Références

Les paragraphes 12.8.4 et 12.8.5 d’ISO 32000-2:2020 décrivent DSS/VRI et les horodatages ; la page physique 606 précise leur traitement DocMDP. La [norme principale conservée](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf) et le [catalogue du bundle](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/sources.json) identifient la source fournie par la PDF Association et sa collection de corrections. `TimestampRequest`, `TimestampResponse` et `TimestampToken` représentent explicitement les données RFC3161.

[Parcours des tutoriels](README.md) · [Signatures modernes](31-pdf20-modern-signature.md) · [Guide du bundle](../pdf-2-0-bundle.md)
