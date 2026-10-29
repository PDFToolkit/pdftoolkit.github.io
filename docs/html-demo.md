# Galerie HTML et conversion locale

Explorez de vrais PDF, leur HTML dérivé, la source PHP ou LaTeX de chaque exemple
et les diagnostics qui expliquent le résultat. La galerie conserve ensemble le
PDF source, les aperçus de ses pages, la source HTML exacte et les empreintes des
fichiers. Son code appartient à la [démo PDF-to-HTML 0.3](https://github.com/PDFToolkit/pdf-to-html-demo),
publiée séparément et utilisant le [convertisseur HTML 0.8](https://pdftoolkit.github.io/fr/modules/to-html/index.html) stable.

## Essayer d’abord un exemple

1. Ouvrez la [démo interactive](https://pdftoolkit.github.io/fr/modules/to-html/demo/) et choisissez un exemple. Aucune installation n’est nécessaire.
2. Utilisez **Voir le résultat** pour comparer le PDF et la page web produite. Des retours à la ligne différents sont normaux : le HTML s’adapte à la largeur disponible.
3. Téléchargez le PDF source pour l’essayer vous-même, ou choisissez votre fichier. Un PDF balisé contient les titres, listes, tableaux et l’ordre de lecture nécessaires au convertisseur ; une simple image numérisée ne fournit pas ces informations.

L’onglet **Code HTML** affiche la sortie originale par défaut. Choisissez **Vue lisible**
pour ajouter une indentation visuelle et une coloration sans modifier son contenu.
La copie et le téléchargement préservent la sortie originale, y compris les
espaces qui comptent dans les formules mathématiques. Les diagnostics expliquent
les informations qui n’ont pas pu être reprises. Une conversion réussie ne
constitue pas un certificat d’accessibilité.

## Convertir un fichier sur cet appareil

Choisissez un PDF pour le convertir directement sur cet appareil, dans votre navigateur.
L’application charge son moteur de conversion depuis ce site.
Elle n’envoie à aucun serveur le PDF choisi, son nom, un mot de passe ou le résultat,
et n’enregistre pas ces valeurs dans le stockage du navigateur. Le chargement de
la page et des fichiers publics du moteur fait toujours des requêtes ordinaires
à l’hébergeur du site.

Chaque conversion dispose d’un nouveau Worker. L’annulation arrête ce Worker.
La taille d’entrée, le temps d’exécution et la mémoire PHP sont bornés ; une entrée
invalide ou non prise en charge produit une erreur ou des diagnostics. Le moteur
publié accepte actuellement au plus 8 Mio de PDF, autorise 30 secondes par
conversion et fixe la limite mémoire PHP à 128 Mio. Les documents développés
pour l’aperçu sont aussi bornés à 16 millions de caractères. Fermer ou recharger la page
efface la session. Le convertisseur est conçu pour le PDF balisé : la ressemblance
visuelle avec une source quelconque non balisée n’est pas garantie.

Le résultat affiché est isolé de la documentation. Les PDF importés n’obtiennent
pas la permission d’exécuter des scripts, de soumettre des formulaires ou de
naviguer dans la page parente. Les téléchargements sont créés localement sur demande.

La démo active explicitement les feuilles de style locales filtrées et combine
les Supplements HTML du catalogue dans leur ordre PDF pour l’interopérabilité
LaTeX. Les scripts PDF et ressources distantes restent bloqués. La bibliothèque
conserve par défaut la sélection stricte du premier Supplement HTML du catalogue ;
les applications choisissent explicitement ces
[politiques de styles](https://pdftoolkit.github.io/fr/modules/to-html/policies.html).

## Lire les exemples visuels

Les onze exemples couvrent la structure, les tableaux et listes, MathML, les valeurs
initiales et la réinitialisation des formulaires, les apparences des widgets,
l’état des signatures, un graphique rendu et les images JPEG, JPEG 2000 et JBIG2
décodées. Comparez l’aperçu de la page source avec le HTML dérivé, puis examinez
la source de génération et les diagnostics. Le téléchargement
HTML contient la sortie réelle de la conversion. L’aperçu du PDF fournit une
référence visuelle ; il ne prouve pas une identité de mise en page au pixel près.

L’[exemple MathML LaTeX](https://pdftoolkit.github.io/fr/modules/to-html/demo/?sample=mathml-se)
utilise un véritable PDF produit par LuaLaTeX avec des éléments mathématiques
dans son arbre de structure, plutôt qu’un fichier MathML associé. Comparez les
fractions et exposants en ligne ou hors texte ainsi que la matrice, puis
téléchargez la source LaTeX et la provenance du build. L’autre exemple MathML
démontre un fichier associé. Ces fixtures montrent les parcours testés ; elles
ne certifient pas tous les PDF LaTeX.

Les capacités explicites de l’application sont décrites pour chaque exemple.
La rastérisation des graphiques et la vérification des signatures nécessitent une
implémentation ou un certificat sélectionné ; leur démonstration ne signifie pas
que les fichiers importés disposent automatiquement de ces capacités. Un résultat
d’intégrité de signature ne prouve ni la confiance dans le certificat, ni sa
validité au moment de signer, ni la permission des modifications ultérieures.
Consultez le [guide graphique](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html)
et le [guide des signatures](https://pdftoolkit.github.io/fr/modules/to-html/signatures.html).

Seul l’exemple publié de réinitialisation active le moteur borné du projet dans
son aperçu isolé. Son script est choisi parmi les fichiers vérifiés de l’exemple.
Son empreinte exacte autorise son exécution. Il réalise l’action de
réinitialisation autorisée et n’exécute pas l’ECMAScript du PDF. Les autres résultats de la galerie et tous les fichiers importés utilisent
un aperçu dont les scripts sont désactivés.

## Examiner et reproduire le résultat

Chaque carte propose le PDF source, le texte HTML, la source PHP ou LaTeX et le JSON des
diagnostics. Le manifeste public de la galerie conserve les empreintes et les
identités des sources. Sans JavaScript, la page propose toujours les aperçus
rendus et ces téléchargements. L’application et son moteur sont sélectionnés
indépendamment de la documentation et des packages PHP.

Pour une application PHP, suivez le
[tutoriel de conversion exécutable](https://pdftoolkit.github.io/fr/tutorials/35-deriver-html.html).
Le [guide des politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html)
et le [guide de couverture](https://pdftoolkit.github.io/fr/modules/to-html/coverage.html)
expliquent les choix d’interprétation et les mécanismes pris en charge.
