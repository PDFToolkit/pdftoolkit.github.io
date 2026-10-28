# Galerie HTML et conversion locale

Explorez de vrais PDF, leur HTML dérivé, le code PHP qui produit chaque exemple
et les diagnostics qui expliquent le résultat. La galerie conserve ensemble le
PDF source, les aperçus de ses pages, la source HTML exacte et les empreintes des
fichiers. Son code appartient à la [démo PDF-to-HTML](https://github.com/PDFToolkit/pdf-to-html-demo),
publiée séparément et utilisant le [convertisseur HTML](https://pdftoolkit.github.io/fr/modules/to-html/index.html) stable.

## Convertir un fichier sur cet appareil

Choisissez un PDF pour exécuter le convertisseur PHP dans un Worker du navigateur.
L’application charge son moteur PHP/WebAssembly et ses dépendances depuis ce site.
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

## Lire les exemples visuels

Les exemples couvrent la structure, les tableaux et listes, MathML, les valeurs
initiales et la réinitialisation des formulaires, les apparences des widgets,
l’état des signatures et un graphique rendu. Comparez l’aperçu de la page source
avec le HTML dérivé, puis examinez l’exemple PHP et les diagnostics. Le téléchargement
HTML contient la sortie réelle de la conversion. L’aperçu du PDF fournit une
référence visuelle ; il ne prouve pas une identité de mise en page au pixel près.

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

Chaque carte propose le PDF source, le texte HTML, le code PHP et le JSON des
diagnostics. Le manifeste public de la galerie conserve les empreintes et les
identités des sources. Sans JavaScript, la page propose toujours les aperçus
rendus et ces téléchargements. L’application et son moteur sont sélectionnés
indépendamment de la documentation et des packages PHP.

Pour une application PHP, suivez le
[tutoriel de conversion exécutable](https://pdftoolkit.github.io/fr/tutorials/35-deriver-html.html).
Le [guide des politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html)
et le [guide de couverture](https://pdftoolkit.github.io/fr/modules/to-html/coverage.html)
expliquent les choix d’interprétation et les mécanismes pris en charge.
