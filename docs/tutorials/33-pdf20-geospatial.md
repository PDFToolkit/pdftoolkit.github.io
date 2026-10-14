# 33. Objets géospatiaux PDF 2.0

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-geospatial.php) dessine deux panneaux illustratifs et associe des données de mesure géospatiales à la page, à un Form XObject et à une image. Une région déclare un système géographique ; l’autre un système projeté. Ce sont deux régions de démonstration indépendantes, pas la conversion d’une même carte topographique.

Dessiner une grille ne crée pas une sémantique géographique. Le script construit séparément les systèmes de coordonnées, couples de points de contrôle, viewports de mesure, unités préférées et nuage de points qui décrivent les objets PDF.

## Exécuter l’exemple

Depuis une copie du core 0.7.0 :

```bash
php examples/pdf20-geospatial.php geospatial.pdf
```

L’exemple fournit Courier avec des [métriques explicites](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/fixtures/pdf20-courier-font.php) : FirstChar/LastChar, largeurs ASCII et FontDescriptor. PDF 2.0 ne permet plus d’omettre ces entrées pour les quatorze polices standard. Cette construction n’incorpore pas de programme de fonte ; un profil exigeant l’incorporation demande une fonte explicitement incorporée.


L’exemple utilise uniquement des objets PDF natifs. Il ne nécessite ni convertisseur d’images, ni convertisseur de fontes, ni base SIG, ni exécutable de projection. Un lecteur peut afficher la page sans proposer d’outils de mesure géographique ; l’aperçu montre bien le dessin réel.

## Déclarer explicitement les systèmes de coordonnées

```php
$geographic = new G\GeographicCoordinateSystem(new G\EpsgCode(4326));
$projected = new G\ProjectedCoordinateSystem(new G\EpsgCode(3857));
```

Ici, `G` est l’alias de `PDF\Document\Geospatial` dans le script. Un `GeographicCoordinateSystem` accepte exactement un code EPSG ou une chaîne WKT. Un `ProjectedCoordinateSystem` exige au moins l’un des deux. WKT est fourni par `AsciiString` ; la bibliothèque ne télécharge aucun registre, n’analyse pas toute la grammaire WKT et ne déduit pas une projection du dessin.

Modifier un identifiant ne recalcule pas les points de contrôle. Il faut fournir des coordonnées appartenant réellement au système choisi. `GeographicPosition` conserve la latitude avant la longitude ; `ProjectedPosition` conserve l’abscisse est avant l’ordonnée nord. Les valeurs doivent être finies et la latitude comprise entre −90 et 90 degrés. Aucune branche arbitraire de longitude n’est imposée.

## Synchroniser les points locaux et réels

`GeospatialControlPoint` associe une `LocalPosition` à une position réelle. `GeospatialControlPoints` construit `/LPTS` et `/GPTS` à partir des mêmes couples, empêchant les longueurs différentes et les mélanges de dimensions ou de natures de coordonnées.

```php
$point = new G\GeospatialControlPoint(
    new G\LocalPosition(new N(0), new N(0)),
    new G\GeographicPosition(new N(48.85), new N(2.34)),
);
```

L’exemple utilise quatre points de contrôle par région. Les coordonnées locales à deux dimensions appartiennent au carré unité de l’objet. `GeospatialBounds` fournit le polygone normalisé délimitant la zone utile ; il ne remplace pas le rectangle du viewport dans les coordonnées de la page. La variante 3D utilise des triplets dans les contextes 3D/RichMedia permis, avec une validation distincte plutôt qu’une conversion implicite de toutes les mesures en trois dimensions.

## Donner son véritable propriétaire à chaque mesure

`GeospatialMeasure` écrit `/Type /Measure`, `/Subtype /GEO`, le système de coordonnées et les tableaux appariés. Un `Viewport` fournit le `/BBox` dans l’espace de la page, un nom facultatif et cette mesure ; `Viewports` fournit le tableau `/VP` de la page.

Lorsque des viewports se superposent, `Viewports::forPoint()` sélectionne le dernier contenant le premier point de la mesure. `Viewport::local()` convertit un point de page en coordonnées locales normalisées. Aucune de ces opérations n’effectue une projection géographique.

Le panneau gauche peint un Form XObject avec ses propres `/Measure` et `/PtData` ; celui de droite peint une image d’un pixel avec son propre `/Measure`. Leurs matrices de dessin positionnent l’illustration indépendamment des métadonnées géospatiales. Les contrôles du graphe effectif couvrent aussi les dictionnaires génériques et remplacements incrémentaux : ajouter les entrées manuellement ne contourne pas les règles de contexte ou de version.

## Ajouter unités, matrice et données de points

`PreferredDisplayUnits` reçoit dans cet ordre une enum linéaire, une enum de surface et une enum angulaire. L’exemple choisit mètres, mètres carrés et degrés. Ces préférences décrivent l’affichage des mesures par un lecteur, pas les unités des opérateurs graphiques de la page.

`ProjectedCoordinateSystemMatrix` contient exactement douze coefficients numériques. Elle applique le vecteur ligne `[x y z 1]` avec la dernière colonne implicite `[0 0 0 1]` et prend priorité sur GPTS dans un système projeté. Sa méthode `transform()` réalise ce calcul affine ; elle ne convertit pas une projection cartographique en une autre.

`PointDataNames` nomme les colonnes du nuage ; chaque tuple `PointData` possède exactement cette largeur. Le tuple LAT/LON/ALT de démonstration contient 48.86, 2.35 et 35. `PointDataCollection` associe ces nuages à un viewport. Les données de colonnes et les opérateurs de dessin restent des objets indépendants.

## Contrôler les relations sérialisées

`tools/validate_pdf20_geospatial.py` lit indépendamment GCS/GPTS/LPTS, Bounds, PDU, PCSM, viewports, propriétaires Form/image et nuages de points à l’aide de pypdf et qpdf. Il contrôle les sorties initiales, incrémentales et linéarisées dans les trois formats de références croisées, y compris leurs préfixes historiques et de repli.

```bash
python tools/validate_pdf20_geospatial.py \
  --php php --qpdf qpdf --work-dir /tmp/pdf20-geospatial
```

Pour explorer le modèle, déplacez un viewport, changez ses unités préférées ou ajoutez un couple de points. Gardez les tuples synchronisés et choisissez explicitement la nature des coordonnées. Un outil SIG indépendant reste nécessaire pour établir la justesse de mesures réelles, du sens WKT ou d’une conversion de projection.

## Références

Les paragraphes 12.9 et 12.10 d’ISO 32000-2:2020, tableaux 265–272, pages physiques 611–622, décrivent ces objets. L’[original conservé](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf) contient les annotations EC3. Le profil natif consigne explicitement l’issue 358 comme `Completed` et les issues 533, 534 et 284 comme `Accepted` ; leurs autorités d’approbation distinctes restent visibles dans le catalogue.

[Parcours des tutoriels](README.md) · [Guide du bundle](../pdf-2-0-bundle.md) · [Couverture](../coverage.md)
