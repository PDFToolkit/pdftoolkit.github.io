# Révisions natives protégées

Ce guide décrit les opérations natives de révisions protégées du core 0.10.0.

Une signature valide protège les octets signés. Elle ne détermine pas seule si
les changements suivants sont autorisés. Le writer natif vérifie les signatures
historiques, classe toute la modification émise et croise les restrictions
DocMDP, FieldMDP, verrous Adobe et droits d’usage authentifiés applicables.
Le [tutoriel du formulaire certifié](tutorials/37-protected-form-fill.md) présente
une opération complète et son résultat visible.

## Conserver le véritable historique natif

Utiliser la `FileRevision` renvoyée par l’écriture native ou la signature vérifiée
dans la même exécution. Snapshots fournis au constructeur, clones, sérialisation
PHP et octets d’un PDF externe ne recréent pas son autorité d’émission.
`PreparedSignature::finalize()` complète les octets réservés, mais des octets
opaques seuls ne prouvent aucun historique vérifié. La vérification lie les octets
finaux, le dictionnaire de signature, l’unique intervalle Contents, ByteRange et
le certificat effectif.

Chaque point d’entrée d’`IncrementalUpdate` et appel direct à `IncrementalWriter`
utilise le même garde. Supprimer `Perms`, remplacer `Root`, détacher l’AcroForm ou
renommer un champ n’efface aucune restriction historique. Le lecteur optionnel
inspecte des PDF externes ; il ne les convertit pas en historiques authentifiés
du writer natif.

## Choisir une opération prise en charge

Les opérations du classificateur sont bornées et soumises à toutes les autres
restrictions historiques. Un niveau de permission n’autorise pas l’édition générale.

| Opération | Périmètre natif protégé |
| --- | --- |
| Remplir un champ `Tx` existant | P2/P3 ; texte simple direct, valeurs par défaut/actions/drapeaux fixes, ReadOnly hérité et verrous conservés, `MaxLen`/comb contrôlés. |
| Remplir un champ `Ch` existant | P2/P3 ; options fixes, valeur et `I`/`TI` ordonnés cohérents avec la version PDF choisie. |
| Changer un `Btn` case/radio | P2/P3 ; `V`, `AS` des widgets et apparences Off/actif existantes concordent. Boutons poussoirs et remplacement de leurs programmes exclus. |
| Remplacer une apparence de texte/choix | Conserver géométrie, liaisons de ressources et chaque octet hors d’une région de texte variable isolée ; voir ci-dessous. |
| Ajouter/modifier/détacher une annotation | P3 seulement ; sous-types et entrées listés, page propriétaire et ordre des annotations restantes inchangés. |
| Ajouter une signature native | Champ non signé existant, réservation inchangée ou nouveau champ terminal unique ; la preuve complète de signature reste distincte. |
| Ajouter des preuves DSS/horodatage documentaire | Preuve de maintenance PDF 2.0 ; verrous Adobe P1 supplémentaires et droits d’usage non desserrés. |
| Instancier un modèle de page | Non implémenté par ce classificateur natif. |
| Mélanger remplissage/annotations et signature/maintenance | Refusé ; séparer en révisions individuellement autorisées. |

La liste d’annotations admises est `Text`, `FreeText`, `Line`, `Square`, `Circle`,
`Polygon`, `PolyLine`, `Highlight`, `Underline`, `Squiggly`, `StrikeOut`, `Caret`,
`Ink` et `Stamp`. ReadOnly, Locked et LockedContents interdisent la modification.
Widgets, nouvelles actions, nouvelles relations et dépendances étrangères ne
reçoivent aucune autorité d’annotation. Le détachement conserve l’objet historique.

Identités des champs, noms qualifiés, structure parent/enfant, drapeaux/valeurs
par défaut hérités et propriétaires des widgets sont comparés aux révisions figées.
Seuls les changements de valeur et de sélection classifiés sont permis. Une valeur
terminale ne contourne ni un parent en lecture seule ni un verrou FieldMDP.
Noms ambigus, renommage, changement de parent, alias supplémentaires et objets
non classifiés sont refusés. Les nouvelles apparences ont des identités neuves ;
flux partagés et ressources historiques restent immuables. Un remplissage
n’autorise jamais à changer le contenu de page.

## Conserver la frontière du texte variable

Pour une apparence de texte/choix non enrichie, la procédure ISO remplace une
région `/Tx BMC`…`EMC` correspondant ; sans région, elle l’ajoute à la fin. Le
classificateur natif conserve chaque octet décodé du préfixe/suffixe et la géométrie.
Les instructions possèdent leur isolation `q`/`Q`. Le contenu marqué seul ne
sauvegarde pas l’état graphique ; chemins, clipping en attente et objets texte
ne traversent ni la région ni les frontières de restauration graphique.

L’analyse lexicale bornée reconnaît commentaires, noms/chaînes échappés et
conteneurs : un faux `EMC` dans une chaîne n’élargit pas la région remplaçable.
Elle accepte les octets bruts ou un `FlateDecode` sans prédicteurs. Les limites
par défaut sont 1 Mio encodé et décodé, 100 000 tokens et une imbrication de 64.
Tx multiples/imbriqués, images inline, opérateurs inconnus et opérateurs de glyphes
Type3 sont refusés. Les noms de ressources gardent leurs liaisons ; les noms
ajoutés désignent uniquement des objets historiques inchangés. Alternatives
d’apparence et noms d’états existants sont conservés ; ajouter R/D ou un état
sans programme historique comparable est refusé. C’est une preuve
de régions/états, pas une validation complète du langage graphique ni la preuve
que les glyphes correspondent à la valeur. Texte enrichi et régénération
arbitraire des apparences restent hors périmètre.

## Autoriser UR3 explicitement à chaque mise à jour

L’historique UR3 natif non chiffré avec transformation `V=2.2` exige une
`UsageRightsAuthorization` choisie par l’application. Le callback
`UsageRightsAuthority::permits()` reçoit la vraie `VerifiedRevisionSignature` ;
ses `facts` exposent les algorithmes vérifiés et le certificat signataire lié.
L’application décide si cette identité peut accorder des droits d’usage.
Validité mathématique, politique autodéclarée du PDF ou simple présence d’un
certificat n’établissent ni cette autorité ni la confiance PKI.

```php
use PDF\Document\Signatures\UsageRightsAuthorization;
use PDF\Document\Signatures\Policies\UsageRight;
use PDF\Syntax\FileStructure\IncrementalUpdate;

$authorization = new UsageRightsAuthorization($authority, UsageRight::FillField);
$update = new IncrementalUpdate($nativeRevision, $replacementBody, null, null, $authorization);
$next = $update->toRevision();
```

`$authority` implémente explicitement `UsageRightsAuthority` dans l’application ;
`$nativeRevision` et `$replacementBody` sont le véritable historique natif et les
objets préparés. La sélection non vide d’opérations vaut pour cette seule mise à
jour. Chaque remplissage, création/modification/suppression d’annotation ou
signature appartient aux droits signés et à cette sélection, tout en respectant
les restrictions DocMDP/FieldMDP/Adobe.

La sauvegarde est évaluée séparément par opération. En ISO 1.7, `FillIn` non
restrictif exige `FullSave` signé ; un droit d’annotation sans rapport ne peut
fournir sa sauvegarde. Droits restrictifs, modification d’annotations et signature
réelle conservent leurs règles prévues. `FillField` applicatif autorise un
remplissage persisté si la politique signée le permet ; il n’exige pas en plus
`FullSave` applicatif lorsque le droit signé fournit seulement cette condition.

PDF 2.0 accepte ici uniquement `P=true` explicite et restrictif. Sa sémantique
différente de `P=false`/absent n’est pas assimilée à ISO 1.7. `UR` ancien, historique
UR chiffré, signatures non vérifiées/opaques, refus d’autorité et opérations de
maintenance/sauvegarde générale non classifiées restent refusés. UR est déprécié
en PDF 2.0 ; chaîne PKI et révocation restent du ressort de l’application.

## Lire les preuves et leurs limites

La matrice de validation indépendante utilise pyHanko 0.37.0 inchangé, qpdf et
Poppler sous PHP 8.3/8.4/8.5. Par runtime : 97 refus natifs, 148 PDF contrôlés,
32 combinaisons natives et 32 remplissages indépendants, quatre chaînes
d’annotations P3 et 198 pixels. UR3 ajoute huit sources signées, trois
remplissages autorisés et 11 CMS vérifiés indépendamment ; altérer un octet signé
est détecté. Ces comptes sont des preuves CMS, structure et rendu, pas 148
approbations de politique ni une décision indépendante d’autorité d’usage.

| Observation indépendante | Interprétation |
| --- | --- |
| pyHanko confirme 16 combinaisons `Tx`/`Ch` | Ces changements de valeur concordent avec sa politique de modification inchangée. |
| Les 32 sorties de boutons remplis et 12 opérations P3 renvoient `OTHER` et `docmdp_ok=false` | Valeurs, états, CMS et pixels sont vérifiés séparément ; la politique de l’oracle n’est pas modifiée. |
| Deux changements ReadOnly passent pyHanko | Le classificateur natif les refuse ; ReadOnly et FieldMDP sont distincts. |
| Le tutoriel 37 renvoie `OTHER` | L’AP modifié appartient à un widget enfant sans `/T` ; les preuves CMS/ByteRange et de rendu n’impliquent pas une approbation DocMDP pyHanko. |
| pyHanko strict refuse de valider les signatures hybrides | Sa matrice utilise Table/Stream ; les tests hybrides natifs restent séparés. |

Les sources sont ISO 32000-1:2008, pages physiques 440–444, 478–482 et 485 ;
ISO 32000-2:2020 EC3, pages physiques 545–549, 560, 588–592, 606 et 607–608 ;
et le supplément Adobe, page physique 43. Le catalogue conservé du core
`resources/signature-revisions/coverage.json` contient leurs SHA-256 exacts.
Modèles de pages, création/suppression générales de champs, nouvelles ressources,
classification de chaînes externes, validation graphique complète et revue
humaine de l’apparence/intention restent des limites explicites.

[Tutoriel du formulaire certifié](tutorials/37-protected-form-fill.md) · [Sécurité](security.md) · [Révisions incrémentales](tutorials/11-incremental-update.md)
