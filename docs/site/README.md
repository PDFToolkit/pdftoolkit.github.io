# Construire la documentation

Le site est publié à [pdftoolkit.github.io](https://pdftoolkit.github.io/) depuis
le dépôt [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io).
Il présente le core et les trois modules optionnels à partir des versions
publiées sélectionnées dans le manifeste. Le commit des textes et des outils de documentation
est indiqué séparément des versions et commits des packages documentés.

## Sources et génération

Ce dépôt conserve les guides, tutoriels, assets partagés, outils de construction
et workflow de publication. Les sources PHP, exemples, tests, ressources de la
spécification et PDF Adobe restent dans leurs dépôts de packages. La construction
les lit dans un checkout complet du core préparé sous `_sources/pdf`, avec ses
modules installés par Composer depuis leurs distributions publiées.

Le manifeste `resources/sources.json` utilise `schemaVersion: 1`. Sa liste
`packages` décrit chaque package avec `name`, `repository`, `version`, `revision`
et `optional`. Ce fichier fait autorité pour les versions et commits documentés.
Les pages et le manifeste de site conservent ces identités séparément du commit
de ce dépôt.

Le checkout du core doit conserver ses PDF originaux, `resources/`, `examples/`,
`composer.lock` et `vendor/`. Une archive Composer ne fournit pas toutes les
références Adobe ni toutes les fixtures nécessaires. Installer les dépendances
de développement depuis ce checkout en conservant son lock ; l'exporteur vérifie
que les versions et révisions des modules installés correspondent au manifeste.
Le core sélectionné utilise Packagist pour résoudre ses modules ; une application
qui utilise ces bibliothèques les installe avec les commandes du
[guide des packages](../packages.md), sans construire le site.

`tools/export_api.php` charge l'autoloading du core préparé et découvre les
classes, interfaces, enums et traits de son `src/` et des modules installés.
Il exporte leurs signatures, propriétés, constantes et provenance par package.
Il lit les expressions des paramètres par défaut sans instancier les objets
qu'elles décrivent. Les liens vers les sources utilisent les commits du
manifeste, y compris pour le core.

`tools/build_site.py` lit les textes et assets depuis `--content-root`, puis
les exemples, ressources normatives et originaux depuis `--source-root`.
Il assemble l'API et les métadonnées de `resources/iso32000-1/` et
`resources/adobe-supplement-iso32000/` du core pour créer les fiches de composants,
index par famille et recherche. Les définitions conservent leurs contraintes,
tableau, document et page de référence. Les entrées composées distinguent les
sources Adobe et ISO ; voir le [guide de couverture](../coverage.md).

Les guides propres aux modules sont publiés sous `/modules/reader/`,
`/modules/images/` et `/modules/fonts/`. Leur package qualifie les pages et liens
pour que les fichiers Markdown de même nom restent distincts.

Chaque script de `examples/` du core doit avoir un tutoriel ou une recette et
un PDF. Le site présente les explications, le rendu de toutes les pages, le code
complet et le PDF généré. Les PDF Adobe sont également accessibles depuis les
fiches de la norme. Le manifeste de site `specificationSources` conserve leurs
noms, empreintes SHA-256, nombres de pages et chemins de téléchargement ; le
vérificateur compare les octets publiés aux originaux.

Les exemples de modules sont déclarés dans `EXTERNAL_EXAMPLES` du générateur.
Le tutoriel 12 lit `examples/pages.php` et
`tests/Fixtures/page-tree/classic.pdf` dans le module lecteur installé. Il publie
les octets du PDF d'entrée, ses trois aperçus et la sortie console de lecture.
Leur provenance utilise le commit du lecteur fixé dans le manifeste ; le core
conserve ses exemples de génération.

Le pilote ISO 32000-2:2020 EC3 est lu dans `resources/iso32000-2-2020/`.
Ses fiches API utilisent une édition explicite au lieu du seul numéro de tableau.
`privateSpecificationSources` conserve l’identité de source et l’URL de métadonnées
publiées sans téléchargement PDF. La copie privée personnalisée n’est jamais
copiée dans la sortie du site. La leçon 27 utilise un PDF réellement généré et
le module de fontes sélectionné.

## Construction locale

PHP 8.3 ou supérieur, Composer, Python 3.13, Poppler (`pdftoppm`) et qpdf 12.4.2
sont utilisés par le workflow. Les dépendances Python sont verrouillées avec
leurs empreintes. Le site publié est statique.

Depuis la racine de ce dépôt, préparer le checkout du core au commit du
manifeste, puis exécuter la même construction complète que la CI :

```sh
core_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['repository'])")
core_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['revision'])")
core_alias=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['version'].rsplit('.', 1)[0]+'.x-dev')")
git clone "$core_repository" _sources/pdf
git -C _sources/pdf checkout --detach "$core_revision"
COMPOSER_ROOT_VERSION="$core_alias" composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python tools/build_docs.py --source-root _sources/pdf --docs-revision "$(git rev-parse HEAD)" --remote
```

Sous PowerShell :

```powershell
$sourceManifest = Get-Content resources/sources.json -Raw | ConvertFrom-Json
$coreSource = $sourceManifest.packages | Where-Object name -eq 'roukmoute/pdf'
git clone $coreSource.repository _sources/pdf
git -C _sources/pdf checkout --detach $coreSource.revision
$env:COMPOSER_ROOT_VERSION = ($coreSource.version -replace '\.\d+$', '.x-dev')
composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
$docsRevision = git rev-parse HEAD
python tools/build_docs.py --source-root _sources/pdf --docs-revision $docsRevision --remote
```

`tools/build_docs.py` vérifie les commits et tags publiés, les sources conservées
et les générations normatives. Il exporte l'API, exécute tous les exemples,
vérifie leurs PDF avec qpdf et les lecteurs indépendants, rend chaque page,
construit le site et contrôle ses liens. `--docs-revision` attend le SHA complet
de 40 caractères du commit de documentation ; il ne remplace pas les révisions
de packages du manifeste. Les chemins des outils peuvent être précisés avec
`--php`, `--qpdf` et `--pdftoppm`.

Pour reconstruire seulement le rendu depuis des entrées déjà validées :

```sh
php tools/export_api.php _build/api.json _sources/pdf resources/sources.json
python tools/build_site.py --content-root . --source-root _sources/pdf --sources resources/sources.json --docs-revision "$(git rev-parse HEAD)" --api _build/api.json --pdf-dir _build/pdfs --pdf-preview-dir _build/pdf-pages --output _site --base-path /
python tools/check_site.py _site
```

Utiliser un dossier de sortie vide lorsque des pages sont supprimées ou
renommées. Le générateur ne supprime pas les fichiers d'un dossier existant ;
le vérificateur signale les pages obsolètes. `_sources/`, `_build/` et `_site/`
sont des dossiers de travail ignorés par Git.

## Aperçu et vérification

Le site central utilise `--base-path /` pour la publication et l'aperçu local :

```sh
python -m http.server 8000 --directory _site
```

Ouvrir [localhost:8000](http://localhost:8000/) pour vérifier navigation,
recherche, menu mobile, aperçus et téléchargements. Poppler rend les images
de chaque page du PDF. Un lecteur PDF natif est également proposé dans une
section dépliable ; son fonctionnement dépend du navigateur. Les boutons
d'ouverture et de téléchargement restent disponibles sur chaque exemple.

`tools/check_site.py` vérifie l'inventaire des pages, fichiers liés, ancres,
unicité des identifiants, titres principaux, recherche, couverture des packages
et couples PDF/source. Le manifeste `exampleSources` distingue les PDF générés
des entrées de lecture, avec les empreintes des PDF, sources et sorties console.
Le vérificateur contrôle les liens de provenance, l'échappement de la sortie
console et les trois pages de l'entrée. Toutes les sources de packages sont
liées à leurs commits publiés ; le commit de documentation conserve sa propre
provenance.

Les tests et contrôles des mécanismes PHP restent dans le dépôt du core et
les dépôts des modules. La CI du core valide ses exemples sous PHP 8.3, 8.4 et
8.5. Depuis le checkout du core, les contrôles Python utilisent ses fichiers
de dépendances verrouillés et ses scripts `tools/validate_mechanisms.py`,
`tools/validate_adobe_supplement.py` et `tools/validate_adobe_encryption.py`.
Les contrôles de chiffrement nécessitent au moins qpdf 12.1.

## Publication

Le workflow Pages de ce dépôt prépare les sources aux révisions du manifeste,
installe leurs dépendances verrouillées, exporte l'API, produit et valide les
PDF, rend leurs pages avec Poppler, construit le site avec `--base-path /`
et exécute le vérificateur avant déploiement. Les permissions d'écriture Pages
et d'identité sont réservées au job de déploiement.

Le dépôt central possède la publication à la racine. L'ancien site de projet
`/pdf/` conserve des redirections de ses routes HTML vers les routes centrales,
en transmettant les paramètres de requête et fragments. Ses anciens
téléchargements binaires restent accessibles. Les dépôts de packages
conservent leurs sources, tests, versions et CI ; leurs changements ne modifient
la référence publiée qu'après mise à jour explicite du manifeste central.

Les HTML et PDF générés sont produits pendant la construction. Pour ajouter
un exemple de génération, écrire le script dans son dépôt de package, puis
le tutoriel ou la recette dans ce dépôt et déclarer sa route dans
`tools/build_site.py`. La vérification échoue si un script du core n'a pas de
page correspondante. Pour un exemple de module, déclarer son package, ses
chemins source/entrée et son nombre attendu de pages dans `EXTERNAL_EXAMPLES`,
puis conserver sa sortie console et ses aperçus pendant la construction.

## Langues de la documentation

L’anglais est publié à la racine ; les pages françaises sont sous `/fr/`. Les
textes anglais communs sont dans `docs/en/` ; les guides originaux de `docs/`
sont en français. Les packages conservent leurs guides anglais avec leur code
et les versions françaises sous `docs/fr/` ou dans `README.fr.md`,
`SECURITY.fr.md` et `CHANGELOG.fr.md`.

Ajouter ou modifier les deux traductions ensemble, avec la même hiérarchie de
 titres. `tools/localization.py` contient les traductions explicites de
l’interface et les routes de langue. Le générateur associe les identifiants des
 titres pour le sélecteur, conserve les anciens liens de section français et
consigne le chemin et le hash de la véritable source traduite. Les exemples
PDF et références originales sont partagés sans modification.

Exécuter `node tests/site_locales.cjs` et le contrôle complet du site. Ils
vérifient le sélecteur, les filtres de recherche, les ancres de section, les
messages de copie, les deux inventaires API, les variantes réciproques et les
adresses de compatibilité.