# Construire la documentation

Le site est publié à [pdftoolkit.github.io](https://pdftoolkit.github.io/) depuis
le dépôt [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io).
Il présente le core, les modules PDF optionnels, la dérivation HTML et les modèles indépendants OpenType et Codecs à partir des versions
publiées sélectionnées dans le manifeste. Le commit des textes et des outils de documentation
est indiqué séparément des versions et commits des packages documentés.

## Sources et génération

Ce dépôt conserve les guides, tutoriels, assets partagés, outils de construction
et workflow de publication. Les sources PHP, exemples, tests, ressources de la
spécification et PDF Adobe restent dans leurs dépôts de packages. La construction
les lit dans un checkout complet du core préparé sous `_sources/pdf`, avec ses
modules PDF installés par Composer depuis leurs distributions publiées. Les packages OpenType et Codecs proviennent de checkouts séparés sous `_sources/opentype` et `_sources/pdf-codecs`, aux commits et tags publiés dans le même manifeste. Leurs installations indépendantes ne modifient ni le core ni son lock.

Le module Images documenté provient aussi d'un checkout séparé, `_sources/pdf-images`,
passé à `--images-root`. Ses guides et déclarations API sont lus au tag publié exact ;
son namespace `PDF\Images\` est chargé depuis ce checkout, sans repli sur une
version plus ancienne installée dans le core. Ses oracles utilisent son propre
`composer.lock` et son autoloader. Les exemples du core gardent leurs dépendances
publiées, même si leur version Images diffère de la version documentée.
`executionDependencies` dans `site-manifest.json` et `validation-sources.json`
distingue `coreExamples`, `imagesValidation` et `htmlValidation`, avec les versions
et commits réellement verrouillés pour chaque exécution.

Le manifeste `resources/sources.json` utilise `schemaVersion: 1`. Sa liste
`packages` décrit chaque package avec `name`, `repository`, `version`, `revision`
et `optional`. Ce fichier fait autorité pour les versions et commits documentés.
Les pages et le manifeste de site conservent ces identités séparément du commit
de ce dépôt.

Le checkout du core doit conserver ses PDF originaux, `resources/`, `examples/`,
`composer.lock` et `vendor/`. Une archive Composer ne fournit pas toutes les
références Adobe ni toutes les fixtures nécessaires. Installer les dépendances
de développement depuis ce checkout en conservant son lock ; l'exporteur vérifie
que les versions et révisions des modules documentés correspondent au manifeste.
Le core sélectionné utilise Packagist pour résoudre ses modules ; une application
qui utilise ces bibliothèques les installe avec les commandes du
[guide des packages](../packages.md), sans construire le site.

Les dix-huit PDF de référence Adobe, ISO et complémentaires originaux sont rangés
dans `resources/reference-documents/` du core. Les métadonnées enregistrent chaque
chemin séparément du nom et de l’empreinte du fichier original. Le générateur lit
ces chemins en conservant les URL publiques de téléchargement existantes. Les
fixtures de tests et exemples générés restent auprès de leurs tests et scripts.

`tools/export_api.php` charge l'autoloading du core préparé et découvre les
classes, interfaces, enums et traits de son `src/`, des modules PDF installés et des checkouts Images, OpenType et Codecs. Il charge les autoloadings propres des deux packages indépendants OpenType et Codecs ; Images et Reader utilisent des chargeurs limités à leurs sources sélectionnées, avec refus des déclarations déjà chargées depuis un autre arbre.
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
`/modules/images/`, `/modules/fonts/`, `/modules/opentype/`, `/modules/codecs/` et `/modules/to-html/`. Leur package qualifie les pages et liens
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

Le checkout PDF vers HTML est fixé séparément sous `_sources/pdf-to-html`.
Les sources du lecteur sont choisies séparément dans le consumer core ou HTML
installé : version et commits source/dist du lock et de l’installation doivent
correspondre exactement au pin Reader. Le core est préféré ; HTML sert de repli
pour les anciennes sélections. Aucun lock publié ne change. Le tutoriel 35 exécute son vrai CLI sur la fixture balisée produite
indépendamment. La construction vérifie les octets de référence et de fixture,
puis exécute l'oracle pypdf/HTML5 du package. Elle copie chaque ressource du JSON
CLI en contrôlant noms, SHA-256 et collisions de sortie. `derivedHtml` reste hors
de l'inventaire des pages documentaires bilingues et apparaît dans un sandbox
sans permission. Les guides/API du module sont sous `/modules/to-html/`.

Le guide d'authentification est accessible sous `/modules/reader/` et
`/modules/to-html/` ; le guide GPOS/variations natif est sous
`/modules/opentype/positioning.html`. Tous ont une version française réciproque.
Le tutoriel 36 exécute le véritable `pdf17-secure-redaction.php` du core et publie
ses deux pages de résultat. La construction vérifie séparément octets et pixels
source/résultat avec qpdf, pypdf et Poppler ; sa copie source privée n'est jamais
publiée comme résultat caviardé. Les identités d'annotations EC3 et fils
d'approbation sont vérifiés contre le PDF canonique inchangé, indépendamment de
la génération des dictionnaires.

Le tutoriel 37 exécute `protected-form-fill.php` du core sélectionné : certification
native P2, verrou FieldMDP historique et remplacement isolé d’apparence Tx.
La construction complète lance aussi `validate_incremental_permissions.py` avec
les exécutables PHP, qpdf et Poppler choisis. Refus natifs, mises à jour hostiles
indépendantes, faits CMS UR3 et pixels restent dans
`_build/incremental-permissions-validation/` ; ce ne sont pas des fixtures de
tutoriel publiées. Le rapport conserve les limites pyHanko sur boutons/widgets,
annotations P3, ReadOnly et hybrides stricts, séparément des mathématiques CMS et
des décisions applicatives d’autorité accordant les droits.

Le guide du MAC source du lecteur est publié sous `/modules/reader/source-mac.html`
et dans sa version française. La construction complète exécute l'oracle MAC
source indépendant de ce lecteur sélectionné avec son véritable core verrouillé,
puis vérifie répartition/PMD/placement d'apparences de codes-barres et usages des
glyphes Type 3 sélectionnés depuis le checkout du core retenu. Elle vérifie aussi
les apparences obligatoires PDF 2.0, dictionnaires d'états et cas licite d'un état
non correspondant avec l'oracle de huit PDF publié. Les rapports et
fixtures hostiles/sources restent dans les répertoires privés du build, hors
des ressources de tutoriels publiées. Les motifs de test des codes-barres ne
prouvent aucune symbologie ; le rapport Type 3 conserve la différence observée
de Poppler en mode 7 sans la transformer en résultat de conformité.

Le guide de clé publique est publié sous `/modules/reader/public-key-authentication.html`
et `/fr/modules/reader/public-key-authentication.html`. Le build exécute
`validate_public_key_authentication.py` et `validate_public_key_aliases.py`
contre le lecteur installé sélectionné et le véritable autoloader de son consumer. Les contrôles indépendants
pyHanko/cryptography couvrent CMS, clés des filtres, droits destinataire, MAC,
quatre cas de métadonnées/alias physiques et deux flux EFF implicites à clés
distinctes. Un mauvais credential de pièce jointe doit permettre l'ouverture
du document puis échouer à son accès. Certificats générés et entrées adverses
restent des données privées du build.

La sélection actuelle documente PDF vers HTML 0.7.0 et le lecteur 0.7.0. Le
[registre des exigences](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html),
les [politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html) et
les [graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html)
distinguent règles natives, adaptations HTML et capacités explicites de
rasterisation, d'authentification et de codecs supplémentaires.

HTML 0.7.0 publie aussi ses [règles de placement MathML et sa procédure de validation navigateur](https://pdftoolkit.github.io/fr/modules/to-html/coverage.html#placement-mathml-et-rendu-navigateur).
La qualification de sa version et un job CI dédié vérifient la sortie dérivée
dans Chromium et Firefox et conservent rapports et captures. HTML 0.7 vérifie aussi les widgets, les attributs dérivés et les popovers de statut des signatures dans les deux moteurs. Le build du site
rend ces guides publiés et vérifie leurs liens. Le build indépendant de la démo
capture aussi sa galerie dans Chromium et contrôle ses pages intégrées dans les deux moteurs.

L'authentification R=2–7 native est une sélection explicite du lecteur. L'oracle
indépendant du package HTML déchiffre de vraies fixtures qpdf et analyse le HTML
dérivé pour vérifier permissions user/owner, mauvais credentials et réutilisation
du convertisseur. L'oracle HTML de clé publique vérifie séparément six sources
balisées indépendantes, masques destinataire, MAC autonome/attaché à une signature,
mauvais certificats, intégrité requise et réutilisation avec une entrée claire.
Ses fixtures temporaires restent dans l'espace de validation.

`tools/build_docs.py` reproduit les tables de glyphes et les fixtures inline/fax,
puis exécute les oracles HTML5/pypdf, les comparaisons de pixels Poppler pour
graphiques/contextes/fax et apparences de widgets, le contrôle des parents d'ancres et le runtime Node.
Il exécute aussi les exemples 02/03/04/05 d'export de figure, de reset ciblé `/DV`,
de dérivation authentifiée avec MAC exigé et d’intégrité de signature source avec
un certificat choisi explicitement. L’oracle de signature emploie des parseurs
PDF/CMS indépendants et vérifie les frontières de révision signée complète ; il
n’établit ni la confiance PKI ni les permissions des changements ultérieurs. L'oracle MAC/HTML5 indépendant
vérifie chemins natif/fourni, identité source, politiques et permissions effectives.
Le reset n'active pas ECMAScript PDF. Ces quatre sorties et leurs ressources restent dans
`_build/pdfs/html-validation/` ; elles n'ajoutent ni pages ni assets au site.

Le catalogue ISO 32000-2:2020 EC3 est lu dans `resources/iso32000-2-2020/`.
Ses fiches API utilisent une édition explicite au lieu du seul numéro de tableau.
`repositorySpecificationSources` conserve l’identité du fichier original, son empreinte, sa taille, ses pages et les liens vers le PDF et ses métadonnées au commit documenté du core. L’original est public dans ce dépôt après autorisation de redistribution confirmée ; les 19 Mo ne sont pas dupliqués dans la sortie du site. La construction vérifie les octets d’origine avant de publier ce lien. La leçon 27 utilise un PDF réellement généré et le module de fontes sélectionné.

`bundleSpecificationSources` consigne séparément les onze originaux complémentaires
à partir de `resources/iso32000-2-bundle/sources.json`. Leurs noms, identités d’octets,
pages physiques et provenance PDF Association sont vérifiés avant publication de
liens vers le commit du dépôt. Les PDF sources restent hors des ressources du site
et des archives Composer. Les fiches API distinguent résumés du projet traduits
et extraits normatifs originaux en anglais. Inventaire complet des tableaux de
base et conformité complète sont deux champs distincts du manifeste.

La construction vérifie le compilateur du catalogue ISO2, le générateur PHP et
la matrice TS 32005, puis exécute les oracles de métadonnées, AES-GCM/CMS/MAC,
horodatages/DSS et contenu balisé. L’exemple d’horodatage reçoit l’exécutable
choisi explicitement par `--openssl`. Tous les exemples possèdent des explications
anglaises/françaises et de véritables rendus PDF.

## Construction locale

PHP 8.3 ou supérieur en 64 bits, Composer, Python 3.13, Node 24.22.1, OpenSSL, Poppler (`pdftoppm`) et qpdf 12.4.2
sont utilisés par le workflow. Les dépendances Python sont verrouillées avec
leurs empreintes. Le site publié est statique.

La construction complète des oracles demande aussi Ghostscript, `prlimit` (util-linux), ImageMagick/libpng, libjbig2dec, FreeType et les bibliothèques/outils de compilation utilisés par l’oracle couleur Poppler épinglé. La liste des paquets Linux est maintenue dans `.github/workflows/pages.yml`. Poppler 26.10.0 est construit séparément pour les contrôles couleur : les anciennes implémentations CalGray diffèrent de la référence indépendante, sans élargissement des tolérances. `--codecs-root` sélectionne le checkout Codecs exact et `--image-pdftoppm` ce moteur. Les commandes PowerShell ci-dessous décrivent préparation des dépôts/dépendances ; les prérequis natifs des oracles doivent aussi être disponibles dans cet environnement.

Depuis la racine de ce dépôt, préparer le checkout du core au commit du
manifeste, puis exécuter la même construction complète que la CI :

```sh
core_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['repository'])")
core_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['revision'])")
core_alias=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['version'].rsplit('.', 1)[0]+'.x-dev')")
opentype_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/opentype')['repository'])")
opentype_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/opentype')['revision'])")

git clone "$core_repository" _sources/pdf
git -C _sources/pdf checkout --detach "$core_revision"
COMPOSER_ROOT_VERSION="$core_alias" composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
git clone "$opentype_repository" _sources/opentype
git -C _sources/opentype checkout --detach "$opentype_revision"
composer install --working-dir=_sources/opentype --no-interaction --prefer-dist
images_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-images')['repository'])")
images_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-images')['revision'])")
git clone "$images_repository" _sources/pdf-images
git -C _sources/pdf-images checkout --detach "$images_revision"
composer install --working-dir=_sources/pdf-images --no-interaction --prefer-dist
codecs_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-codecs')['repository'])")
codecs_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-codecs')['revision'])")
git clone "$codecs_repository" _sources/pdf-codecs
git -C _sources/pdf-codecs checkout --detach "$codecs_revision"
composer install --working-dir=_sources/pdf-codecs --no-interaction --prefer-dist
html_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-to-html')['repository'])")
html_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-to-html')['revision'])")
git clone "$html_repository" _sources/pdf-to-html
git -C _sources/pdf-to-html checkout --detach "$html_revision"
composer install --working-dir=_sources/pdf-to-html --no-interaction --prefer-dist
demo_repository=$(python -c "import json; print(json.load(open('resources/demo-source.json'))['repository'])")
demo_revision=$(python -c "import json; print(json.load(open('resources/demo-source.json'))['revision'])")
git clone "$demo_repository" _sources/pdf-to-html-demo
git -C _sources/pdf-to-html-demo checkout --detach "$demo_revision"
composer install --working-dir=_sources/pdf-to-html-demo --no-dev --no-interaction --prefer-dist
npm ci --ignore-scripts --prefix _sources/pdf-to-html-demo
npm audit --prefix _sources/pdf-to-html-demo
npx --prefix _sources/pdf-to-html-demo playwright install --with-deps chromium firefox
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/source-integrity-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html-demo/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-images/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/vendor/pdftoolkit/pdf-fonts/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/opentype/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-codecs/tools/jpeg-validation-requirements.txt
reader_consumer=$(python tools/check_sources.py --source-root _sources/pdf --pdf-to-html-root _sources/pdf-to-html --reader-consumer)
python -m pip install --require-hashes -r "$reader_consumer/vendor/pdftoolkit/pdf-reader/tools/source-mac-validation-requirements.txt"
python -m pip check
python _sources/pdf-images/tools/build_poppler.py --output _build/poppler
python tools/build_docs.py --source-root _sources/pdf --opentype-root _sources/opentype --codecs-root _sources/pdf-codecs --images-root _sources/pdf-images --pdf-to-html-root _sources/pdf-to-html --demo-root _sources/pdf-to-html-demo --docs-revision "$(git rev-parse HEAD)" --image-pdftoppm _build/poppler/build/utils/pdftoppm --remote
```

Sous PowerShell :

```powershell
$sourceManifest = Get-Content resources/sources.json -Raw | ConvertFrom-Json
$coreSource = $sourceManifest.packages | Where-Object name -eq 'roukmoute/pdf'
$opentypeSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/opentype'
git clone $coreSource.repository _sources/pdf
git -C _sources/pdf checkout --detach $coreSource.revision
$env:COMPOSER_ROOT_VERSION = ($coreSource.version -replace '\.\d+$', '.x-dev')
composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
git clone $opentypeSource.repository _sources/opentype
git -C _sources/opentype checkout --detach $opentypeSource.revision
composer install --working-dir=_sources/opentype --no-interaction --prefer-dist
$imagesSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/pdf-images'
git clone $imagesSource.repository _sources/pdf-images
git -C _sources/pdf-images checkout --detach $imagesSource.revision
composer install --working-dir=_sources/pdf-images --no-interaction --prefer-dist
$codecsSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/pdf-codecs'
git clone $codecsSource.repository _sources/pdf-codecs
git -C _sources/pdf-codecs checkout --detach $codecsSource.revision
composer install --working-dir=_sources/pdf-codecs --no-interaction --prefer-dist
$htmlSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/pdf-to-html'
git clone $htmlSource.repository _sources/pdf-to-html
git -C _sources/pdf-to-html checkout --detach $htmlSource.revision
composer install --working-dir=_sources/pdf-to-html --no-interaction --prefer-dist
$demoSource = Get-Content resources/demo-source.json -Raw | ConvertFrom-Json
git clone $demoSource.repository _sources/pdf-to-html-demo
git -C _sources/pdf-to-html-demo checkout --detach $demoSource.revision
composer install --working-dir=_sources/pdf-to-html-demo --no-dev --no-interaction --prefer-dist
npm ci --ignore-scripts --prefix _sources/pdf-to-html-demo
npm audit --prefix _sources/pdf-to-html-demo
npx --prefix _sources/pdf-to-html-demo playwright install --with-deps chromium firefox
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/source-integrity-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html-demo/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-images/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/vendor/pdftoolkit/pdf-fonts/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/opentype/tools/validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-codecs/tools/jpeg-validation-requirements.txt
$readerConsumer = python tools/check_sources.py --source-root _sources/pdf --pdf-to-html-root _sources/pdf-to-html --reader-consumer
python -m pip install --require-hashes -r "$readerConsumer/vendor/pdftoolkit/pdf-reader/tools/source-mac-validation-requirements.txt"
python -m pip check
python _sources/pdf-images/tools/build_poppler.py --output _build/poppler
$docsRevision = git rev-parse HEAD
python tools/build_docs.py --source-root _sources/pdf --opentype-root _sources/opentype --codecs-root _sources/pdf-codecs --images-root _sources/pdf-images --pdf-to-html-root _sources/pdf-to-html --demo-root _sources/pdf-to-html-demo --docs-revision $docsRevision --image-pdftoppm _build/poppler/build/utils/pdftoppm --remote
```

Le préflight compare les niveaux de tous les titres FR/EN de l'inventaire qui
sera rendu, avant les oracles coûteux. Une traduction absente ou une structure
différente bloque la construction ; `guide-headings-validation.json` conserve
les routes contrôlées. Le rendu réutilise ce même contrat pour les ancres.

`tools/build_docs.py` vérifie les commits et tags publiés, les sources conservées
et les générations normatives. Il exporte l'API, exécute tous les exemples,
vérifie leurs PDF avec qpdf et les lecteurs indépendants, rend chaque page,
construit le site et contrôle ses liens. `--docs-revision` attend le SHA complet
de 40 caractères du commit de documentation ; il ne remplace pas les révisions
de packages du manifeste. Les chemins des outils peuvent être précisés avec
`--php`, `--qpdf`, `--openssl` et `--pdftoppm`.

Pour reconstruire seulement le rendu depuis des entrées déjà validées :

```sh
reader_consumer=$(python tools/check_sources.py --source-root _sources/pdf --pdf-to-html-root _sources/pdf-to-html --reader-consumer)
php tools/export_api.php _build/api.json _sources/pdf resources/sources.json _sources/opentype _sources/pdf-to-html "$reader_consumer" _sources/pdf-codecs _sources/pdf-images
python tools/build_site.py --content-root . --source-root _sources/pdf --opentype-root _sources/opentype --codecs-root _sources/pdf-codecs --images-root _sources/pdf-images --pdf-to-html-root _sources/pdf-to-html --demo-root _sources/pdf-to-html-demo --demo-build _build/html-demo --sources resources/sources.json --docs-revision "$(git rev-parse HEAD)" --api _build/api.json --pdf-dir _build/pdfs --pdf-preview-dir _build/pdf-pages --output _site --base-path /
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

## Entrées de la dérivation HTML

L'option `--node` permet de choisir l'exécutable Node ; elle vaut `node` par
défaut. Le harness reçoit aussi `--php` pour ses sous-processus de fixtures,
sans dépendre d'un autre PHP trouvé sur le PATH. Les oracles de rendu utilisent
le `--pdftoppm` choisi. Le profil par défaut et les frames du site n'exécutent
pas le runtime ; les cas activés explicitement sont contrôlés dans l'espace privé
de validation. Tous les guides du module conservent leur variante EN/FR.

Le checkout publié `_sources/pdf-to-html` est sélectionné indépendamment. Son core et son lecteur installés doivent correspondre exactement à son propre lock publié (versions et commits source/dist), séparément des pins core/Reader documentés. HTML 0.7.0 exécute ses oracles et le tutoriel 35 avec son lock publié, qui sélectionne Reader 0.7.0. Le Reader 0.7.0 documenté provient du vendor core 0.12.1 ; ses guides, API, tutoriel 12 et oracles utilisent tous cette sélection. Exemples et oracles Reader chargent le véritable core de ce consumer. `_build/validation-sources.json` consigne les deux environnements de validation et leurs commits de packages exacts. L’exporteur API enregistre uniquement les namespaces HTML et lecteur sélectionnés contre leurs arbres choisis. Les guides apparaissent sous `/modules/to-html/` dans les deux langues. Le tutoriel 35 copie le PDF d’entrée, rend toutes ses pages et exécute le CLI pour produire le vrai HTML et les diagnostics JSON. `derivedHtml` inventorie cette sortie séparément des routes documentaires avec package/SHA et frames sandboxées ; le vérificateur refuse le contenu actif dans ces aperçus. L’original fourni de 74 pages reste dans le package, lié au commit de la version retenue.

## Démo dans le navigateur et galerie visuelle

La [page de démo](https://pdftoolkit.github.io/fr/modules/to-html/demo/index.html)
native et sa contrepartie anglaise intègrent une application publiée séparément.
`resources/demo-source.json` sélectionne sa version stable, son tag annoté et le
commit désigné. Cette sélection d’application est distincte :
`resources/sources.json` décrit toujours les seuls packages PHP. Les exemples
exécutables, la génération des fixtures, les fragments d’interface, le JavaScript,
l’assemblage du moteur et les licences restent dans le dépôt de la démo.

`tools/html_demo.py` utilise des objets explicites pour la source, les fichiers,
la galerie et la construction. Le build vérifie le checkout sélectionné et le
tag publié, appelle `tools/build_demo.py` avec PHP, Node, Poppler et le checkout
HTML publié choisis, et refuse une provenance de brouillon. Chaque fichier est
comparé à un inventaire borné de chemins, tailles et SHA-256. L’application copiée
figure dans `htmlDemo` du manifeste du site, séparément des identités des packages
et du `derivedHtml` des tutoriels. Les sources HTML et PHP des exemples portent
les extensions `.html.txt` et `.php.txt` ; aucune sortie brute de l’application
ne devient une page de documentation exécutable.

Les fichiers sont publiés sous `/assets/html-demo/` et partagés entre les langues.
Seules les pages de démo chargent le module JavaScript de l’application et
adaptent leur CSP au WebAssembly local, aux Workers isolés et aux ressources blob.
Le résultat importé s’affiche dans une sandbox vide ; le seul profil explicite
de réinitialisation de la galerie peut activer le moteur vérifié de la
bibliothèque dans une sandbox sans permission de même origine. La permission de
son script inline est une empreinte CSP SHA-256 exacte, recalculée depuis le fichier
de reset sélectionné ; aucun script inline arbitraire n’est autorisé. Les fichiers
compressés du moteur sont aussi vérifiés par tailles décodées bornées et empreintes.
Les autres pages
de documentation conservent leur politique de sécurité actuelle.

La présentation, les guides graphique et signatures affichent des comparaisons
statiques entre les aperçus PDF sources et de vraies captures Chromium du HTML
dérivé. Chaque carte relie l’exemple interactif sélectionné et ses téléchargements
PDF/PHP, sans charger le moteur de démo ni modifier la CSP de ces guides. La galerie
conserve la version du navigateur et les dimensions des images ; le contrôle
complet vérifie ces faits, les octets PNG exacts, les routes bilingues, la provenance,
les inventaires des cas et tous les liens de comparaison. La CI installe aussi la
dépendance Playwright verrouillée de la démo et lance son oracle Chromium/Firefox
sur le site effectivement construit. Rapports et captures sont conservés dans
l’artifact `browser-demo-evidence`. Pour reproduire :

```sh
(cd _sources/pdf-to-html-demo && npx playwright install --with-deps chromium firefox)
python -m http.server 8080 --bind 127.0.0.1 --directory _site
# Dans un autre terminal, une fois le serveur prêt :
node _sources/pdf-to-html-demo/tests/browser.cjs --base-url http://127.0.0.1:8080 --output _build/demo-browsers --site
```

Le contrat existant du manifeste de compatibilité couvre les redirections des
pages natives de démo et copie à l’identique les fichiers `.txt`, JSON, JS, CSS,
WASM, ZIP, PDF et PNG inventoriés. L’application possède sa propre release ; le
site central ne la sélectionne qu’après publication et qualification de cette
release. Le tag annoté du site suit les contrôles du commit exact, du déploiement
et de la compatibilité.

Le build complet exécute aussi `tools/validate_demo.py` de la démo publiée avec
`--require-release` : les contrôles indépendants PDF, HTML5 et PNG conservent leur
rapport dans `_build/html-demo-validation.json`. Installer ses dépendances de
validation hashées dans le même environnement d’oracles avant la construction.
