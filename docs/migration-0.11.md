# Migration vers le core 0.11

Le core 0.11 étend les révisions natives protégées et applique de nouvelles
corrections EC3 reliées aux sources. Choisir explicitement les politiques de
construction lors du passage d'une application à PDF 2.0. L'édition effective
de l'en-tête/catalogue source reste l'autorité du writer ; une option de
constructeur ne la remplace pas.

## Remplacer les groupes documentaires par des parents explicites

`DocumentPart::addGroup()` devient `addChildren($first, ...$others)`. Chaque appel
ajoute des frères à un tableau `/DParts` plat et ordonné. Pour représenter un groupe,
construire un parent et lui attacher ses enfants explicitement. Cycles, enfants
répétés et feuilles de pages avec enfants sont refusés, sans attacher une partie
d'un lot invalide.

Déplacer le XMP `Metadata` DPart vers `DocumentPartRoot` ; il est désormais interdit
sur DPart, y compris dans les objets incrémentaux conservés. Garder les données
métier dans `DocumentPartMetadata` (`/DPM`). Le constructeur racine reçoit
`NameType|MetadataEntry ...$entries` après son nœud et le niveau d'enregistrement
facultatif. Renommer les arguments nommés `nodeNames:` en `entries:` ; les noms de
niveau positionnels gardent leur sens. DPM accepte aussi les valeurs `NameType`
UTF-8 décodées, même imbriquées/indirectes. Les clés suivent toujours XML Name.
Voir le [tutoriel 28](tutorials/28-pdf20-metadata-declarations.md).

## Traiter les noms Type3 nullables et les politiques versionnées

Un `FontDescriptor` Type3 peut omettre `FontName` : sa propriété `fontName` devient
nullable. Appeler `requiredName()` lorsque le code exige un nom. Les autres
sous-types en exigent toujours un. Le `Name` conservé d'un Type3 et le nom de son
descripteur doivent être cohérents.

Choisir `ButtonFieldSemantics::Pdf20` pour les apparences radio PDF 2.0 sans `Off`,
ou les valeurs `V`/`DV` conservées des boutons poussoirs. La sémantique historique
reste celle par défaut. Une case à cocher exige toujours `Off` ; `AS` et la valeur
effective restent cohérents. Un `NullType` texte explicite est conservé physiquement,
mais traité comme absent lors de la résolution des valeurs héritées.

Choisir `SignatureSeedSemantics::Pdf20` pour les seeds PDF 2.0 et fournir
`IntegerType` pour `V`. `LockDocument`, `AppearanceFilter` et la capacité 3 natifs
PDF 2.0 n'exigent plus de déclaration d'extension Adobe. Le défaut historique
conserve la capacité réelle et les règles Adobe. Le chemin de signature figé
vérifie à nouveau l'édition réelle. La sélection intrinsèque du digest EdDSA et
la règle historique DSA/SHA1 restent distinctes ; le backend prouve toujours sa
sortie réelle.

## Fournir du XMP UTF-8 décodé en PDF 2.0

Fournir le XMP comme octets UTF-8 décodés, avec d'éventuels filtres de compression
explicites. Une déclaration XML annonçant un autre encodage est refusée. Des
métadonnées pré-encodées opaques ne prouvent pas cet encodage et sont refusées
en PDF 2.0. La construction habituelle de `MetadataStream` avec un `XmpPacket`
explicite est conservée.

Les révisions natives gardent une preuve d'encodage immuable liée aux octets du
flux émis. Conserver un flux comprimé ne relit pas un builder mutable et ne traite
pas les octets comprimés comme du texte. Le passage d'un document PDF 1.7 conservé
à PDF 2.0 vérifie aussi ses métadonnées selon la nouvelle exigence. Ce contrôle
porte sur l'encodage demandé par EC3 #296 ; il ne prouve pas la conformité aux
schémas XML ou XMP.

## Authentifier chaque mise à jour UR3 chiffrée

Fournir un `PasswordUsageRightsAuthentication` ou `CertificateUsageRightsAuthentication`
à chaque `UsageRightsAuthorization`, avec l'autorité applicative d'octroi et les
opérations sélectionnées. Encodage/handler du mot de passe ou déchiffreur de
certificat sont explicites. Une clé fournie par l'appelant, une précédente mise
à jour réussie ou la simple présence d'un identifiant ne donnent aucune autorité.

```php
$authorization = new UsageRightsAuthorization(
    $authority,
    UsageRight::FillField,
    new CertificateUsageRightsAuthentication($recipientDecrypter),
);
```

Des filtres cryptographiques nommés avec d'autres identités utilisent
`CryptFilterUsageRightsCredential`. Le writer natif authentifie toutes les clés
déclarées et intersecte les permissions de portée documentaire. C'est plus strict
que l'accès différé aux pièces jointes du Reader. L'accès propriétaire ou public-key
complet ne remplace jamais UR, DocMDP, FieldMDP ni le périmètre applicatif.
Créer un champ terminal de signature exige aussi `UsageRight::AddField` et la
permission réelle de création, indépendamment de celle de signer.

Un remplissage UR3 restrictif PDF 2.0 exige désormais `Document.FullSave` signé ;
`FillIn` seul ne suffit pas. Ne pas réécrire la déclaration signée pour ajouter
ce droit. `P=false`/absent PDF 2.0 suit sa propre sémantique en conservant identité
vérifiée, périmètre applicatif explicite et restrictions DocMDP/FieldMDP. L'édition
source signée gouverne ces règles, pas une mise à niveau ultérieure du catalogue.

## Choisir explicitement texte enrichi, valeurs indirectes et modèles

Le remplissage enrichi utilise `RichTextFilling(new WtPdfXmlRichTextParser())`
et le couple `V`/`RV`. Le parseur borné vérifie leur équivalence sans réseau ni
entités XML. Chaque widget affecté nécessite une nouvelle apparence normale
complète ; le dessin fourni par l'appelant n'est pas automatiquement certifié
équivalent au texte. Ressources historiques, géométrie et verrous restent fixes.

Les chaînes/flux texte indirects exigent un propriétaire figé exclusif à l'entrée
du champ et un décodage borné. `PageTemplateInstantiation` ajoute une copie prouvée
d'une page invisible historique `Names/Templates`, avec ressources inchangées et
sans clonage de champs/annotations. P1 le refuse ; UR applicable exige
`SpawnTemplate` et le droit de sauvegarde. Ces droits ne permettent pas de modifier
librement le graphe.

Conserver la véritable `FileRevision` native issue de l'écriture/signature.
L'[historique physique Reader 0.6](https://pdftoolkit.github.io/fr/modules/reader/revision-history.html)
expose préfixes et identités source sans créer d'autorité de modification pour le
core. UR ancien, import arbitraire d'historiques externes, modification générale
des champs et nouvelles ressources d'apparence libres restent non supportés.
Le [guide des révisions protégées](protected-revisions.md) détaille contrôles,
exemples, divergences des oracles indépendants et frontières restantes.

[Couverture](coverage.md) · [Audits des sources](source-audits.md) · [Sécurité](security.md)
