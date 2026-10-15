# 37. Remplir un formulaire certifié

Ce tutoriel utilise le core 0.11.0. Son code PHP complet et son PDF généré
proviennent du checkout core sélectionné pour le site ; le dépôt
de documentation ne contient aucune seconde implémentation.

L’exemple signe un PDF avec DocMDP P2, verrouille `Reference` par FieldMDP, puis
remplace la valeur `Response` de `Pending` par `Reviewed`. La deuxième révision
remplace aussi son apparence textuelle visible. Contenu de page, ancienne
apparence, ressources et chaque octet signé restent inchangés.

## Exécuter l’exemple natif

Depuis un checkout core contenant `examples/protected-form-fill.php`, ses
dépendances de développement verrouillées et fixtures publiques de signature,
avec PHP 8.3+ et OpenSSL :

```sh
php examples/protected-form-fill.php protected-form-fill.pdf
qpdf --check protected-form-fill.pdf
```

Le résultat comporte une page montrant `Reviewed` dans son cadre gris d’origine.
Le code ci-dessous provient du package core sélectionné, avec son lien de source
exact. Le certificat et la clé privée sont des fixtures publiques de test ;
l’exemple démontre les mathématiques de signature, pas la confiance du certificat.

## Établir les restrictions signées

```php
$author = new SignatureFieldSigning(
    $backend,
    new PartialFieldName(new TextString('Certification')),
    new SignatureCapacity(8192),
    new SignatureSigningIntent(
        certification: DocMdpPermissions::FormFillingTemplatesAndSigning,
    ),
    lock: new SignatureFieldLock(
        SignatureLockAction::Include,
        new ArrayType(new TextString('Reference')),
    ),
);
```

Le script complet lie cette politique au vrai catalogue et à l’AcroForm avant
signature. P2 permet le remplissage implémenté ; FieldMDP protège toujours
`Reference`. La `SignedRevision` native conserve la vérification réelle de sortie.
Garder son objet `revision` dans la même exécution. Reconstruire une `FileRevision`
depuis les octets ou compléter un `finalize()` opaque ne recrée pas cette autorité.

## Préparer seulement les remplacements classifiés

```php
$fieldRecord = $signed->revision->binding($field);
$widgetRecord = $signed->revision->binding($widget);
$fieldDictionary = $fieldRecord->dictionary ?? throw new LogicException('The signed field retains its dictionary.');
$widgetDictionary = $widgetRecord->dictionary ?? throw new LogicException('The signed widget retains its dictionary.');
$update = new IncrementalUpdate($signed->revision, new FileBody(
    new IndirectObject(
        $fieldDictionary->with($entry('V', new TextString('Reviewed'))),
        $fieldRecord->identifier,
    ),
    new IndirectObject(
        $widgetDictionary->with($entry('AP', new DictionaryType(
            $entry('N', new IndirectReference($appearance('Reviewed'))),
        ))),
        $widgetRecord->identifier,
    ),
));
$filled = $update->toRevision();
```

`$entry` et `$appearance` sont les constructeurs explicites du script complet.
Champ et widget gardent leurs identités. L’apparence de remplacement reçoit une
identité neuve et référence la police historique inchangée. Le garde compare
aussi chaque autre objet figé : lister deux remplacements n’autorise aucun
changement étranger d’un flux de contenu ou d’une ressource.

Les octets signés d’origine restent un préfixe exact. La nouvelle section xref
sélectionne valeur et apparence actualisées en conservant la révision précédente.
Une mise à jour incrémentale garde l’ancien contenu : elle n’efface pas les secrets.

## Isoler le texte modifié

L’apparence dessine son cadre gris avant la région `/Tx BMC`…`EMC`. Celle-ci possède
une séquence équilibrée `q`, `BT`…`ET`, `Q` pour `Reviewed`. Ancien et nouveau
programmes conservent chaque octet décodé hors de cette région, ainsi que géométrie
et liaisons des noms de ressources. `BMC`/`EMC` seuls ne sauvegardent pas l’état
graphique. Chemins, clipping en attente et objets texte ne traversent pas les
frontières protégées.

L’opération ne reconstruit pas les apparences de boutons et n’ajoute aucun état
ou alternative sans programme historique comparable. Elle ne prouve pas non plus
que des glyphes arbitraires représentent visuellement la valeur. Le
[guide des révisions protégées](../protected-revisions.md) liste les champs,
sous-types d’annotations, limites lexicales et autorité UR3 explicite.

## Vérifier ce que prouve le résultat

qpdf contrôle la syntaxe ; le rendu montre le nouveau texte et le cadre conservé.
La vérification CMS/ByteRange indépendante contrôle la signature sur les octets
d’origine. La politique de modification pyHanko inchangée renvoie `OTHER` pour
cet exemple, car l’AP modifié appartient à un widget enfant sans `/T`. Ce constat
est une limite d’oracle, pas une approbation DocMDP revendiquée de pyHanko.

Changer ensemble `Response` et son apparence Tx pour essayer un autre remplissage.
Modifier `Reference`, le texte de page ou la police historique doit être refusé.
P1 n’autorise pas le remplissage, et ajouter signature ou DSS au même remplissage
sort des preuves d’opération séparées. Import de chaînes externes, modèles, texte
enrichi, nouvelles ressources, validation PKI et interprétation humaine restent
hors de cet exemple.

[← 36. Caviardisation](36-applied-redaction.md) · [Révisions natives protégées](../protected-revisions.md) · [Tous les tutoriels](README.md)
