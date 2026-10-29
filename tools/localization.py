"""Explicit site translations and stable locale routes.

Markdown prose is translated in source files. This catalogue only translates the
site's generated interface; PHP snippets and original normative text are kept.
"""

from html import escape
from html.parser import HTMLParser
import re

LANGUAGES = ('en', 'fr')
# Public directory URLs already linked by the released Codecs README.
PUBLISHED_ROUTE_ALIASES = {
    'modules/reader/image-codecs/index.html': 'modules/reader/image-codecs.html',
    'fr/modules/reader/image-codecs/index.html': 'fr/modules/reader/image-codecs.html',
}
ENGLISH_ROUTES = {
    'guides/mecanismes.html': 'guides/mechanisms.html',
    'guides/supplement-adobe.html': 'guides/adobe-supplement.html',
    'guides/references-adobe.html': 'guides/adobe-references.html',
    'guides/demarrer.html': 'guides/getting-started.html',
    'guides/composants.html': 'guides/components.html',
    'guides/modules.html': 'guides/packages.html',
    'guides/couverture.html': 'guides/specification.html',
    'guides/securite.html': 'guides/security.html',
    'guides/revisions-protegees.html': 'guides/protected-revisions.html',
    'guides/signalements.html': 'guides/reporting.html',
    'guides/versions.html': 'guides/changelog.html',
}
GROUP_ROUTES = {
    'objets': 'objects', 'fichier': 'file', 'contenu': 'content',
    'document': 'document', 'fonctions': 'functions', 'filtres': 'filters',
    'lexique': 'lexical-conventions', 'norme': 'specification',
    'dictionnaires': 'dictionaries', 'entrees': 'entries', 'definitions': 'definitions',
    'adobe': 'adobe', 'iso2': 'pdf-2-0', 'securite': 'security', 'polices-externes': 'external-fonts',
    'images-externes': 'external-images', 'lecture': 'reader', 'fontes-opentype': 'opentype', 'conversion-html': 'to-html', 'codecs-images': 'image-codecs',
}
ENGLISH_ROUTES.update({f'reference/groups/{old}.html': f'reference/groups/{new}.html' for old, new in GROUP_ROUTES.items()})
for module in ('reader', 'images', 'fonts', 'opentype', 'to-html', 'codecs'):
    ENGLISH_ROUTES[f'modules/{module}/signalements.html'] = f'modules/{module}/reporting.html'
    ENGLISH_ROUTES[f'modules/{module}/versions.html'] = f'modules/{module}/changelog.html'


# Project-authored pilot summaries, translated independently of original normative prose.
ISO2_DESCRIPTIONS_FR = {'Identifies the document catalog.': 'Identifie le catalogue du document.',
 '(Required except for the stated conditions in PDF 2.0; optional in PDF 1.2 through 1.7) An appearance dictionary. In PDF 2.0 it is required except for Rect[0]==Rect[2] AND Rect[1]==Rect[3], or Subtype Popup, Projection or Link. AP.N defines the normal appearance; state dictionaries require a name AS. An unmatched state retains the processor fallback defined in 12.5.5.':
     '(Obligatoire sauf dans les cas indiqués en PDF 2.0 ; optionnel en PDF 1.2 à 1.7) '
     'Dictionnaire d’apparences. En PDF 2.0, il est obligatoire sauf si '
     'Rect[0]==Rect[2] ET Rect[1]==Rect[3], ou si Subtype vaut Popup, Projection ou Link. '
     'AP.N définit l’apparence normale ; les dictionnaires d’états exigent un nom AS. '
     'Un état sans correspondance conserve le comportement de repli du lecteur décrit en 12.5.5.',
 'A catalog-level PDF version declaration later than the file header.': 'Déclare dans le catalogue une version '
                                                                        'PDF plus récente que celle de l’en-tête.',
 'Developer extension declarations, held in a direct dictionary.': 'Déclarations d’extensions des développeurs, '
                                                                   'conservées dans un dictionnaire direct.',
 'An indirect reference to the root page-tree node.': 'Référence indirecte vers le nœud racine de l’arbre des '
                                                      'pages.',
 'Page-label ranges with an entry for the first page.': 'Plages de libellés de pages, avec une entrée pour la '
                                                        'première page.',
 'Document name trees; the encrypted-wrapper conditions are separate graph rules.': 'Arbres de noms du document ; '
                                                                                    'les conditions des '
                                                                                    'enveloppes chiffrées '
                                                                                    'relèvent de règles de graphe '
                                                                                    'séparées.',
 'An indirect dictionary of named destinations.': 'Dictionnaire indirect de destinations nommées.',
 'Preferences controlling document presentation.': 'Préférences de présentation du document.',
 'Initial arrangement of displayed pages.': 'Disposition initiale des pages affichées.',
 'Initial document viewing mode.': 'Mode initial de consultation du document.',
 'An indirect reference to the outline hierarchy root.': 'Référence indirecte vers la racine de la hiérarchie des '
                                                         'signets.',
 'An indirect array of article-thread dictionaries.': 'Tableau indirect de dictionnaires de fils de lecture '
                                                      'd’articles.',
 'Initial action or destination.': 'Action ou destination initiale.',
 'Document-wide additional actions.': 'Actions supplémentaires portant sur tout le document.',
 'Document-level URI action information.': 'Informations documentaires pour les actions URI.',
 'Interactive form root.': 'Racine du formulaire interactif.',
 'An indirectly referenced document metadata stream.': 'Flux de métadonnées du document référencé indirectement.',
 'An indirect reference to the logical structure tree root.': 'Référence indirecte vers la racine de l’arbre de '
                                                              'structure logique.',
 'Information about tagged-PDF conventions.': 'Informations sur les conventions du PDF balisé.',
 'Default natural language for document text.': 'Langue naturelle par défaut du texte documentaire.',
 'Historical web-capture information; deprecated in PDF 2.0.': 'Informations historiques de capture web, '
                                                               'dépréciées en PDF 2.0.',
 'Output-intent dictionaries describing rendering conditions.': 'Dictionnaires d’intentions de sortie décrivant '
                                                                'les conditions de rendu.',
 'Document-associated private application data.': 'Données privées d’application associées au document.',
 'Optional-content configuration, required when optional content exists.': 'Configuration du contenu optionnel, '
                                                                           'requise lorsque ce contenu existe.',
 'Document access-permission information.': 'Informations sur les permissions d’accès au document.',
 'Digital-signature legal-content attestations.': 'Attestations de contenu juridique pour les signatures '
                                                  'numériques.',
 'Document requirement dictionaries.': 'Dictionnaires d’exigences documentaires.',
 'Portable-collection presentation; wrapper-specific requirements are separate.': 'Présentation de collection '
                                                                                  'portable ; les exigences des '
                                                                                  'enveloppes sont séparées.',
 'Historical XFA display-regeneration hint; deprecated in PDF 2.0.': 'Indication historique de régénération de '
                                                                     'l’affichage XFA, dépréciée en PDF 2.0.',
 'Document Security Store; validation-data semantics are not implemented by this schema.': 'Document Security '
                                                                                           'Store ; ce schéma '
                                                                                           'n’implémente pas la '
                                                                                           'sémantique des '
                                                                                           'données de '
                                                                                           'validation.',
 'Associated file specifications; their relationships are validated by the native mechanism.': 'Spécifications de '
                                                                                               'fichiers '
                                                                                               'associés, dont '
                                                                                               'les relations '
                                                                                               'sont vérifiées '
                                                                                               'par le mécanisme '
                                                                                               'natif.',
 'An indirect reference to the document-parts hierarchy root.': 'Référence indirecte vers la racine de la '
                                                                'hiérarchie des parties documentaires.',
 'Filespec identifies a file-specification dictionary; EF, EP and RF trigger the required Type entry.': 'Filespec '
                                                                                                        'identifie '
                                                                                                        'une '
                                                                                                        'spécification '
                                                                                                        'de '
                                                                                                        'fichier '
                                                                                                        '; EF, EP '
                                                                                                        'et RF '
                                                                                                        'rendent '
                                                                                                        'l’entrée '
                                                                                                        'Type '
                                                                                                        'obligatoire.',
 'File system used to interpret the specification.': 'Système de fichiers utilisé pour interpréter la '
                                                     'spécification.',
 'Fallback file name, required when platform-specific names are absent.': 'Nom de fichier de repli, requis en '
                                                                          'l’absence de noms propres aux '
                                                                          'plateformes.',
 'Unicode file name preferred over F when present.': 'Nom Unicode préféré à F lorsqu’il est présent.',
 'A historical platform-specific file name, deprecated in PDF 2.0.': 'Nom de fichier historique propre à une '
                                                                     'plateforme, déprécié en PDF 2.0.',
 'Two byte-string identifiers of the referenced file.': 'Deux identifiants du fichier référencé, exprimés comme '
                                                        'chaînes d’octets.',
 'Whether the referenced file is volatile.': 'Indique si le fichier référencé est volatil.',
 'Embedded-file stream bindings; required with related-file bindings.': 'Liaisons de flux de fichiers incorporés, '
                                                                        'requises avec des liaisons de fichiers '
                                                                        'liés.',
 'Related-file arrays matching embedded-file bindings.': 'Tableaux de fichiers liés correspondant aux liaisons '
                                                         'des fichiers incorporés.',
 'Description of the file specification.': 'Description de la spécification de fichier.',
 'An indirect reference to portable-collection item metadata.': 'Référence indirecte vers les métadonnées d’un '
                                                                'élément de collection portable.',
 'An indirectly referenced file thumbnail image.': 'Image de miniature du fichier référencée indirectement.',
 'Encrypted-payload identification; required for encrypted-wrapper payloads.': 'Identification de la charge '
                                                                               'chiffrée, requise pour les '
                                                                               'charges des enveloppes chiffrées.',
 'Relationship between the referring PDF object or marked content and its associated file.': 'Relation entre '
                                                                                             'l’objet PDF ou le '
                                                                                             'contenu marqué '
                                                                                             'référent et son '
                                                                                             'fichier associé.',
 'Identifies a namespace dictionary when present.': 'Identifie un dictionnaire d’espace de noms lorsque cette '
                                                    'entrée est présente.',
 'Namespace identity, conventionally a URI.': 'Identité de l’espace de noms, généralement une URI.',
 'File specification of the namespace schema.': 'Spécification de fichier du schéma de l’espace de noms.',
 'Namespace-specific role mappings; cross-namespace graph semantics remain separate.': 'Correspondances de rôles '
                                                                                       'propres à l’espace de '
                                                                                       'noms ; la sémantique du '
                                                                                       'graphe entre espaces '
                                                                                       'reste séparée.',
 'One or more associated file specifications, each carrying AFRelationship; use a named property resource.': 'Une '
                                                                                                             'ou '
                                                                                                             'plusieurs '
                                                                                                             'spécifications '
                                                                                                             'de '
                                                                                                             'fichiers '
                                                                                                             'associés, '
                                                                                                             'chacune '
                                                                                                             'avec '
                                                                                                             'AFRelationship '
                                                                                                             '; '
                                                                                                             'utiliser '
                                                                                                             'une '
                                                                                                             'ressource '
                                                                                                             'de '
                                                                                                             'propriétés '
                                                                                                             'nommée.'}


# Project-authored EC3 overlays; original normative descriptions remain untranslated.
ISO2_DESCRIPTIONS_FR.update({
    '(Required; deprecated in PDF 2.0) Security handlers may define their own use of the Length entry and should use it to define the bit length of the file encryption key. The bit length of the file encryption key shall be a multiple of 8 in the range of 40 to 256. The standard security handler expresses the Length entry in bytes (e.g., 32 means a length of 256 bits) and public-key security handlers express it as is (e.g., 256 means a length of 256 bits). When CFM is AESV2, the Length key shall have the value of 128 for public-key security handlers, and 16 for the standard security handler. When CFM is AESV3, the Length key shall have a value of 256 for public-key security handlers, and 32 for the standard security handler. NOTE (2020) The Length key was corrected to be required and the descriptive text updated.':
        '(Obligatoire ; déprécié en PDF 2.0) Les gestionnaires de sécurité peuvent définir leur utilisation de Length et devraient y indiquer la longueur en bits de la clé de chiffrement du fichier, multiple de 8 compris entre 40 et 256. Le gestionnaire Standard exprime Length en octets (32 représente 256 bits), tandis que les gestionnaires à clé publique l’expriment en bits (256 représente 256 bits). Pour CFM=AESV2, Length vaut 128 pour les gestionnaires à clé publique et 16 pour Standard. Pour CFM=AESV3, Length vaut respectivement 256 et 32. NOTE (2020) Length a été rendu obligatoire et sa description mise à jour.',
    '(Required) If the crypt filter is referenced from StmF or StrF in the encryption dictionary, this entry shall be an array of byte strings, where each byte string shall be a binary-encoded CMS object that shall list recipients that have been granted equal access rights to the document. The enveloped data contained in the CMS object shall include both a 20-byte seed value that shall be used to compute the file encryption key (see 7.6.5.3, "Public- key encryption algorithms") followed by 4 bytes of permissions settings (see "Table 24 — Public-key security handler user access permissions") that shall apply to the recipient list. There shall be only one object per unique set of access permissions. If a recipient appears in more than one list, the permissions used shall be those in the first matching list. NOTE (2020) The cross-reference to Table 24 in the above paragraph was corrected. If the crypt filter is referenced from a Crypt filter decode parameter dictionary (see "Table 14 — Optional parameters for Crypt filters"), this entry shall be a byte string that shall be a binary-encoded CMS object that shall contain a list of all recipients who are permitted to access the corresponding encrypted stream. The enveloped data contained in the CMS object shall be a 20-byte seed value that shall be used to create the file encryption key that shall be used by the algorithm in "Algorithm 1: Encryption of data using the RC4 or AES algorithms".':
        '(Obligatoire) Si le filtre cryptographique est référencé par StmF ou StrF du dictionnaire de chiffrement, cette entrée est un tableau de chaînes d’octets. Chacune contient un objet CMS binaire désignant des destinataires ayant les mêmes droits d’accès au document. Les données enveloppées contiennent une graine de 20 octets servant au calcul de la clé du fichier (7.6.5.3), suivie de 4 octets de permissions applicables à cette liste de destinataires (tableau 24). Chaque ensemble de permissions distinct correspond à un seul objet. Si un destinataire figure dans plusieurs listes, la première liste correspondante détermine ses permissions. NOTE (2020) Le renvoi au tableau 24 a été corrigé. Si le filtre est référencé par un dictionnaire de paramètres de décodage Crypt (tableau 14), cette entrée est une chaîne d’octets contenant un objet CMS binaire listant les destinataires autorisés à accéder au flux chiffré correspondant. Les données enveloppées contiennent alors une graine de 20 octets servant à créer la clé utilisée par l’algorithme 1 de chiffrement RC4 ou AES.',
    'Required nonempty array of indirect page or page-tree-node references. Null entries are forbidden.':
        'Tableau obligatoire et non vide de références indirectes vers des pages ou des nœuds de l’arbre des pages. Les entrées nulles sont interdites.',
    'Required integer count of descendant page leaves, at least one.':
        'Nombre entier obligatoire de pages descendantes, au moins égal à un.',
    '(Optional; PDF 1.3; indirect reference preferred; deprecated in PDF 2.0) The digital identifier of the page’s parent Web Capture content set (see 14.10.6, "Object attributes related to web capture").':
        '(Optionnel ; PDF 1.3 ; référence indirecte préférable ; déprécié en PDF 2.0) Identifiant numérique de l’ensemble de contenu Web Capture parent de la page (14.10.6).',
    '(Optional) A 16-byte string that is the checksum of the bytes of the uncompressed embedded file. The checksum shall be calculated by applying the standard MD5 message-digest algorithm (defined in Internet RFC 1321) to the bytes of the embedded file stream. NOTE This is strictly a checksum, and is not used for security purposes.':
        '(Optionnel) Chaîne de 16 octets contenant la somme de contrôle des octets décompressés du fichier incorporé. Elle est calculée en appliquant MD5, défini par la RFC 1321, aux octets du flux incorporé. NOTE Il s’agit uniquement d’une somme de contrôle, sans fonction de sécurité.',
    'Required direct URL string documenting this developer extension. Each extension should receive a unique URL (recommendation, not a mandatory uniqueness constraint).':
        'Chaîne URL directe obligatoire documentant cette extension de développeur. Chaque extension devrait recevoir une URL unique : il s’agit d’une recommandation, sans contrainte obligatoire d’unicité.',
    '(Optional; PDF 1.3; indirect reference preferred; deprecated in PDF 2.0) The digital identifier of the image’s parent Web Capture content set (see 14.10.6, "Object attributes related to web capture").':
        '(Optionnel ; PDF 1.3 ; référence indirecte préférable ; déprécié en PDF 2.0) Identifiant numérique de l’ensemble de contenu Web Capture parent de l’image (14.10.6).',
    'Optional array of radio-button collections. The outer array may be empty to explicitly declare no collections. Every inner array is nonempty and contains indirect optional-content-group references; at most one group per collection is ON, and all may be OFF. Absent values inherit the default configuration as specified by Table 99.':
        'Tableau optionnel de groupes de boutons radio. Le tableau externe peut être vide pour déclarer explicitement l’absence de groupes. Chaque tableau interne est non vide et contient des références indirectes vers des groupes de contenu optionnel ; au plus un groupe de chaque collection est ON, et tous peuvent être OFF. Les valeurs absentes héritent de la configuration par défaut conformément au tableau 99.',
    'Required for non-Type3 fonts. The PostScript name agrees with BaseFont in the referring font or CIDFont. For a Type3 font including a Name entry, a present descriptor FontName agrees with that Name.':
        'Obligatoire pour les polices autres que Type3. Le nom PostScript correspond à BaseFont dans la police ou le CIDFont qui référence ce descripteur. Pour une police Type3 comportant une entrée Name, FontName, s’il est présent dans le descripteur, correspond à ce Name.',
    'Optional integer font weight in the inclusive range 1 to 1000. Values 100, 200, 300, 400, 500, 600, 700, 800 and 900 are recommended. Normal weight is 400 and bold is 700; interpretation varies between fonts.':
        'Poids entier optionnel compris entre 1 et 1000 inclus. Les valeurs 100, 200, 300, 400, 500, 600, 700, 800 et 900 sont recommandées. Le poids normal vaut 400 et le gras 700 ; l’interprétation varie selon les polices.',
    '(Optional; Wipe, Glitter, Fly, Cover, Uncover and Push transition styles only) The direction in which the specified transition effect shall moves, expressed in degrees counterclockwise starting from a left-to-right direction. (This differs from the page object’s Rotate entry, which is measured clockwise from the top.) If the value is an integer, it shall be one of: 0 Left to right 90 Bottom to top (Wipe only) 180 Right to left (Wipe only) 270 Top to bottom 315 Top-left to bottom-right (Glitter only) If the value is a name, it shall be None, which is relevant only for the Fly transition when the value of SS is not 1.0. Default value: 0.':
        '(Optionnel ; uniquement pour les transitions Wipe, Glitter, Fly, Cover, Uncover et Push) Direction du déplacement de l’effet, en degrés antihoraires à partir de la direction gauche-droite. Elle diffère de Rotate, mesuré dans le sens horaire depuis le haut. Un entier vaut 0 pour gauche-droite, 90 pour bas-haut (Wipe), 180 pour droite-gauche (Wipe), 270 pour haut-bas ou 315 pour haut-gauche vers bas-droite (Glitter). Un nom doit être None, uniquement pertinent pour Fly lorsque SS diffère de 1.0. Valeur par défaut : 0.',
    '(Optional; PDF 1.3) A border style dictionary (see "Table 168 — Entries in a border style dictionary") specifying the line width and dash pattern that shall be used in drawing the annotation’s border.':
        '(Optionnel ; PDF 1.3) Dictionnaire de style de bordure (tableau 168) précisant l’épaisseur du trait et le motif de tirets utilisés pour dessiner la bordure de l’annotation.',
    '(Required) The default appearance string that shall be used in formatting the text (see 12.7.4.3, "Variable text"). The annotation dictionary’s AP entry, if present, shall take precedence over the DA entry (see “Table 170 — Entries in an appearance dictionary” and 12.5.5, “Appearance streams”).':
        '(Obligatoire) Chaîne d’apparence par défaut utilisée pour mettre en forme le texte (12.7.4.3). L’entrée AP du dictionnaire d’annotation, si elle est présente, prend priorité sur DA (tableau 170 et 12.5.5).',
    '(Optional; PDF 1.6) A set of four numbers describing the numerical differences between two rectangles: the Rect entry of the annotation and a rectangle contained within that rectangle. The inner rectangle is where the annotation’s text should be displayed. Any border styles and/or border effects specified by BS and BE entries, respectively, shall be applied to the border of the inner rectangle. The four numbers correspond to the differences in default user space between the left, top, right, and bottom coordinates of Rect and those of the inner rectangle, respectively. Each value shall be greater than or equal to 0. The sum of the top and bottom differences shall be less than the height of Rect, and the sum of the left and right differences shall be less than the width of Rect.':
        '(Optionnel ; PDF 1.6) Quatre nombres décrivent les différences entre Rect et un rectangle intérieur où le texte de l’annotation devrait s’afficher. Les styles BS et effets BE s’appliquent à la bordure intérieure. Les nombres représentent, dans l’espace utilisateur par défaut, les différences entre les bords gauche, supérieur, droit et inférieur respectifs. Chaque valeur est positive ou nulle. La somme des différences supérieure et inférieure est strictement inférieure à la hauteur de Rect ; celle des différences gauche et droite est strictement inférieure à sa largeur.',
    '(Optional; PDF 1.5) A set of four numbers that shall describe the numerical differences between two rectangles: the Rect entry of the annotation and the actual boundaries of the underlying square or circle. Such a difference may occur in situations where a border effect (described by BE) causes the size of the Rect to increase beyond that of the square or circle. The four numbers shall correspond to the differences in default user space between the left, top, right, and bottom coordinates of Rect and those of the square or circle, respectively. Each value shall be greater than or equal to 0. The sum of the top and bottom differences shall be less than the height of Rect, and the sum of the left and right differences shall be less than the width of Rect.':
        '(Optionnel ; PDF 1.5) Quatre nombres décrivent les différences entre Rect et les limites réelles du carré ou du cercle sous-jacent. Un effet de bordure BE peut agrandir Rect au-delà de ces limites. Les nombres représentent, dans l’espace utilisateur par défaut, les différences entre les bords gauche, supérieur, droit et inférieur respectifs. Chaque valeur est positive ou nulle. La somme des différences supérieure et inférieure est strictement inférieure à la hauteur de Rect ; celle des différences gauche et droite est strictement inférieure à sa largeur.',
    '(Optional; PDF 1.5) A set of four numbers that shall describe the numerical differences between two rectangles: the Rect entry of the annotation and the actual boundaries of the underlying caret. Such a difference can occur. When a paragraph symbol specified by Sy is displayed along with the caret. The four numbers shall correspond to the differences in default user space between the left, top, right, and bottom coordinates of Rect and those of the caret, respectively. Each value shall be greater than or equal to 0. The sum of the top and bottom differences shall be less than the height of Rect, and the sum of the left and right differences shall be less than the width of Rect.':
        '(Optionnel ; PDF 1.5) Quatre nombres décrivent les différences entre Rect et les limites réelles du signe d’insertion, notamment lorsqu’un symbole de paragraphe Sy l’accompagne. Les nombres représentent, dans l’espace utilisateur par défaut, les différences entre les bords gauche, supérieur, droit et inférieur respectifs. Chaque valeur est positive ou nulle. La somme des différences supérieure et inférieure est strictement inférieure à la hauteur de Rect ; celle des différences gauche et droite est strictement inférieure à sa largeur.',
    '(Optional) A document-wide default value for the DA attribute of variable text fields (see 12.7.4.3, "Variable text").':
        '(Optionnel) Valeur par défaut de DA pour les champs à texte variable dans l’ensemble du document (12.7.4.3).',
    '(Optional) The partial field name (see 12.7.4.2, "Field names").':
        '(Optionnel) Nom partiel du champ (12.7.4.2).',
    '(Required; inheritable) The default appearance string containing a sequence of valid page-content graphics or text state operators that define such properties as the field’s text size and colour.':
        '(Obligatoire ; héritable) Chaîne d’apparence par défaut contenant une séquence valide d’opérateurs graphiques ou d’état du texte, définissant notamment la taille et la couleur du texte du champ.',
    '(Optional; inheritable) An integer greater than or equal to zero specifying the maximum length of the field text, in characters.':
        '(Optionnel ; héritable) Entier positif ou nul précisant la longueur maximale du texte du champ, en caractères.',
    '(Optional; PDF 1.7) An unordered array of acceptable digest algorithm names. Array values are SHA1 (deprecated in PDF 2.0), SHA256, SHA384, SHA512 or RIPEMD160. The default is implementation-specific. It applies to RSA credentials; intrinsic-digest signature algorithms use their algorithm-defined digest.':
        '(Optionnel ; PDF 1.7) Tableau non ordonné de noms d’algorithmes de condensat acceptables : SHA1 (déprécié en PDF 2.0), SHA256, SHA384, SHA512 ou RIPEMD160. Le défaut dépend de l’implémentation. Cette entrée s’applique aux clés RSA ; les algorithmes de signature ayant un condensat intrinsèque utilisent celui défini par leur algorithme.',
    '(Optional) Minimum required seed-value parser capability: 1 recognises PDF 1.5 entries; 2 recognises PDF 1.7 and earlier entries; 3 recognises PDF 2.0 and earlier entries. Ff determines whether this is a required constraint.':
        '(Optionnel) Capacité minimale du lecteur de contraintes de signature : 1 reconnaît les entrées PDF 1.5 ; 2 celles de PDF 1.7 et antérieurs ; 3 celles de PDF 2.0 et antérieurs. Ff détermine si cette contrainte est obligatoire.',
    '(Optional) A set of flags specifying various characteristics of the action (see "Table 240 — Flags for submit-form actions"). Default value: 0.':
        '(Optionnel) Indicateurs précisant les caractéristiques de l’action d’envoi de formulaire (tableau 240). Valeur par défaut : 0.',
    '(Optional; PDF 2.0) Supported values include: utf-8, utf-16, Shift-JIS, BigFive, GBK, or UHC.':
        '(Optionnel ; PDF 2.0) Les valeurs prises en charge comprennent utf-8, utf-16, Shift-JIS, BigFive, GBK et UHC.',
    '(Optional) A set of flags specifying various characteristics of the action (see "Table 242 — Flag for reset-form actions"). Default value: 0.':
        '(Optionnel) Indicateurs précisant les caractéristiques de l’action de réinitialisation de formulaire (tableau 242). Valeur par défaut : 0.',
    '(Required) The ordinal page number on which this annotation shall appear, where page 0 is the first page.':
        '(Obligatoire) Numéro de la page où l’annotation apparaît ; la première page porte le numéro 0.',
    '(Required) The name of the preferred signature handler to use when validating this signature. If the Prop_Build entry is not present, it shall be also the name of the signature handler that was used to create the signature. If Prop_Build is present, it may be used to determine the name of the handler that created the signature (which is typically the same as Filter but is not needed to be). A PDF processor may substitute a different handler when verifying the signature, as long as it supports the specified SubFilter format. Example signature handlers are Adobe.PPKLite, Entrust.PPKEF, CICI.SignIt, and VeriSign.PPKVS. The name of the filter (i.e. signature handler) shall be identified in accordance with the rules defined in Annex E, "Extending PDF".':
        '(Obligatoire) Nom du gestionnaire de signature préféré pour la validation. En l’absence de Prop_Build, il désigne aussi celui qui a créé la signature. Prop_Build peut sinon identifier ce gestionnaire, généralement identique à Filter mais sans obligation. Un lecteur peut employer un autre gestionnaire prenant en charge le format SubFilter. Exemples : Adobe.PPKLite, Entrust.PPKEF, CICI.SignIt et VeriSign.PPKVS. Le nom respecte les règles de l’annexe E.',
    '(Optional) A name that describes the encoding of the signature value and key information in the signature dictionary. A PDF processor may use any handler that supports this format to validate the signature. The following values for public-key cryptographic signatures should be used: adbe.x509.rsa_sha1 (PDF 1.3), adbe.pkcs7.detached (PDF 1.3), adbe.pkcs7.sha1 (PDF 1.4), ETSI.CAdES.detached (PDF 2.0) and ETSI.RFC3161 (PDF 2.0). (PDF 2.0) When the Type of this dictionary is DocTimeStamp, the SubFilter value should be ETSI.RFC3161 and when the Type of this dictionary is Sig (possibly by default) any of the values may be used except ETSI.RFC3161 (see 12.8.3, "Signature interoperability"). Other values may be defined by developers, and when used, shall be prefixed with the registered developer identification. All prefix names shall be registered (see Annex E, "Extending PDF"). The prefix "adbe" and the prefix "ETSI" have been registered by Adobe Systems and ETSI, respectively, and the subfilter names listed above and defined in 12.8.3, "Signature interoperability" and 12.8.5, "Document timestamp (DTS) dictionary" may be used by any developer. The values adbe.x509.rsa_sha1 and adbe.pkcs7.sha1 have been deprecated with PDF 2.0. To support backward compatibility, PDF readers should process these values for this key, but PDF writers shall not use this value for this key.':
        '(Optionnel) Nom décrivant le codage de la signature et des informations de clé. Tout gestionnaire compatible peut valider ce format. Valeurs recommandées : adbe.x509.rsa_sha1 (PDF 1.3), adbe.pkcs7.detached (PDF 1.3), adbe.pkcs7.sha1 (PDF 1.4), ETSI.CAdES.detached (PDF 2.0) et ETSI.RFC3161 (PDF 2.0). En PDF 2.0, Type=DocTimeStamp devrait utiliser ETSI.RFC3161 ; Type=Sig, explicite ou par défaut, peut utiliser les autres valeurs (12.8.3). Les valeurs supplémentaires portent un préfixe de développeur enregistré selon l’annexe E. Les préfixes adbe et ETSI sont enregistrés par Adobe Systems et ETSI ; leurs noms définis en 12.8.3 et 12.8.5 peuvent être utilisés par tout développeur. adbe.x509.rsa_sha1 et adbe.pkcs7.sha1 sont dépréciés en PDF 2.0 : les lecteurs devraient les traiter pour compatibilité, mais les producteurs ne doivent plus les écrire.',
    '(Optional; deprecated in PDF 2.0) A name identifying the digest algorithm when not specified in the certificate. Legacy names are MD5, SHA1, SHA256, SHA384, SHA512 and RIPEMD160. MD5 and SHA1 are deprecated in PDF 2.0. The default for PDF 1.5 through 1.7 is MD5.':
        '(Optionnel ; déprécié en PDF 2.0) Nom du condensat lorsqu’il n’est pas précisé dans le certificat. Valeurs historiques : MD5, SHA1, SHA256, SHA384, SHA512 et RIPEMD160. MD5 et SHA1 sont dépréciés en PDF 2.0. Le défaut pour PDF 1.5 à 1.7 est MD5.',
    'Optional integer permission level: 1 forbids changes; 2 allows form filling, page-template instantiation and signing; 3 additionally allows annotation changes. Default: 2. DSS/document-timestamp maintenance is exempt as specified in the source.':
        'Niveau entier optionnel de permission : 1 interdit les modifications ; 2 autorise le remplissage, l’instanciation de modèles de page et la signature ; 3 autorise aussi les changements d’annotations. Défaut : 2. La maintenance DSS et des horodatages de document bénéficie des exceptions définies par la source.',
    '(Optional; PDF 2.0) If present, shall be DSS for a document security store dictionary.':
        '(Optionnel ; PDF 2.0) S’il est présent, ce nom vaut DSS pour un dictionnaire de stockage des preuves de sécurité du document.',
    '(Optional; PDF 2.0) This dictionary contains Signature VRI dictionaries (see 12.8.4.4, "Validation-related information (VRI)"). The key of each entry in this dictionary is the base-16-encoded (uppercase) SHA-1 digest of the signature to which it appliesa and the value is the Signature VRI dictionary which contains the validation-related information for that signature.':
        '(Optionnel ; PDF 2.0) Dictionnaire de preuves VRI de signatures (12.8.4.4). Chaque clé est le condensat SHA-1 de la signature correspondante, codé en hexadécimal majuscule ; sa valeur est le dictionnaire VRI contenant les informations de validation de cette signature.',
    '(Optional; PDF 2.0) An array of indirect reference to streams, each containing one DER-encoded X.509 certificate (see Internet RFC 5280). This array contains certificates that may be used in the validation of any signatures in the document.':
        '(Optionnel ; PDF 2.0) Tableau de références indirectes vers des flux contenant chacun un certificat X.509 codé en DER (RFC 5280). Ces certificats peuvent servir à valider les signatures du document.',
    '(Optional; PDF 2.0) An array of indirect references to streams, each containing a DER-encoded Online Certificate Status Protocol (OCSP) response (see Internet RFC 6960). This array contains OCSPs that may be used in the validation of the signatures in the document.':
        '(Optionnel ; PDF 2.0) Tableau de références indirectes vers des flux contenant chacun une réponse OCSP codée en DER (RFC 6960). Ces réponses peuvent servir à valider les signatures du document.',
    '(Optional; PDF 2.0) An array of indirect references to streams, each containing a DER-encoded Certificate Revocation List (CRL) (see Internet RFC 5280). This array contains CRLs that may be used in the validation of the signatures in the document.':
        '(Optionnel ; PDF 2.0) Tableau de références indirectes vers des flux contenant chacun une liste de révocation CRL codée en DER (RFC 5280). Ces listes peuvent servir à valider les signatures du document.',
    '(Optional; PDF 2.0) If present, shall be VRI for a validation-related information dictionary.':
        '(Optionnel ; PDF 2.0) S’il est présent, ce nom vaut VRI pour un dictionnaire d’informations de validation.',
    '(Optional; PDF 2.0) An array of (indirect references to) streams, each containing one DER-encoded X.509 certificate (see Internet RFC 5280). This array contains certificates that were used in the validation of this signature.':
        '(Optionnel ; PDF 2.0) Tableau de références indirectes vers des flux contenant chacun un certificat X.509 codé en DER (RFC 5280), utilisé pour valider cette signature.',
    '(Required, if a CRL is present; PDF 2.0) An array of indirect references to streams that are all CRLs used to determine the validity of the certificates in the chains related to this signature. Each stream shall reference a CRL that is an entry in the CRLs array in the DSS dictionary.':
        '(Obligatoire si une CRL est présente ; PDF 2.0) Tableau de références indirectes vers toutes les CRL utilisées pour déterminer la validité des certificats des chaînes associées à cette signature. Chaque flux référence une CRL présente dans le tableau CRLs du dictionnaire DSS.',
    '(Required, if an OCSP is present; PDF 2.0) An array of indirect references to streams that are all OCSPs used to determine the validity of the certificates in the chains related to this signature. Each stream shall reference an OCSP that is an entry in the OCSPs array in the DSS dictionary.':
        '(Obligatoire si une réponse OCSP est présente ; PDF 2.0) Tableau de références indirectes vers toutes les réponses OCSP utilisées pour déterminer la validité des certificats des chaînes associées à cette signature. Chaque flux référence une réponse présente dans le tableau OCSPs du dictionnaire DSS.',
    '(Optional; PDF 2.0) The date/time at which this signature VRI dictionary was created. TU shall be a date string as defined in 7.9.4, "Dates".':
        '(Optionnel ; PDF 2.0) Date et heure de création du dictionnaire VRI, sous forme de chaîne de date conforme à 7.9.4.',
    "(Optional; PDF 2.0) A stream containing the DER-encoded timestamp (see Internet RFC 3161 as updated by Internet RFC 5816) that contains the date/time at which this signature VRI dictionary was created. NOTE 1 The date/time contained in the timestamp token can be used for audit purposes. NOTE 2 The hash value to be contained in the timestamp token is left undefined. For PKCS #7 signatures the datum that is hashed and included in the messageImprint field of the DER encoded timestamp stored in the TS entry (see Internet RFC 3161 as updated by Internet RFC 5816) is the encryptedDigest field in the signature's PKC S#7 object (as defined in Internet RFC 2315).":
        '(Optionnel ; PDF 2.0) Flux contenant un horodatage DER (RFC 3161, mise à jour par RFC 5816) indiquant la date et l’heure de création du dictionnaire VRI. NOTE 1 Cette date peut servir à l’audit. NOTE 2 La valeur à hacher est laissée indéfinie. Pour les signatures PKCS #7, le champ messageImprint de l’horodatage TS contient le condensat du champ encryptedDigest de l’objet PKCS #7 de la signature, défini par la RFC 2315.',
    '(Optional; deprecated in PDF 2.0) A name tree that maps name strings to objects that may be used by applications or scripts to modify the default view of the 3D artwork. The names in this name tree shall be text strings so as to be encoded in a way that will be accessible from ECMAScript.':
        '(Optionnel ; déprécié en PDF 2.0) Arbre de noms associant des chaînes à des objets que des applications ou scripts peuvent utiliser pour modifier la vue 3D par défaut. Ses noms sont des chaînes de texte dont le codage est accessible depuis ECMAScript.',
    'Optional background colour-space name, restricted to DeviceRGB. Default value: DeviceRGB.':
        'Nom optionnel de l’espace colorimétrique du fond, limité à DeviceRGB. Valeur par défaut : DeviceRGB.',
    'Optional array of exactly three numbers in the inclusive range 0.0 to 1.0, giving the background colour in DeviceRGB. Default value: [1 1 1] (white).':
        'Tableau optionnel de trois nombres exactement, compris entre 0.0 et 1.0 inclus, donnant la couleur du fond en DeviceRGB. Valeur par défaut : [1 1 1], blanc.',
    'Optional flag controlling visibility of the intersection between the cutting plane and 3D geometry. True makes it visible; false hides it. Default value: true.':
        'Indicateur optionnel de visibilité de l’intersection entre le plan de coupe et la géométrie 3D. True l’affiche ; false la masque. Valeur par défaut : true.',
    'Optional cutting-plane visibility flag. True makes the cutting plane visible; false hides it. Default: true.':
        'Indicateur optionnel de visibilité du plan de coupe. True l’affiche ; false le masque. Défaut : true.',
    'Required PDF 2.0 content dictionary storing the artwork and its configurations and views. It is unique to each annotation.':
        'Dictionnaire de contenu PDF 2.0 obligatoire, conservant le contenu multimédia, ses configurations et ses vues. Il est propre à chaque annotation.',
    'Optional PDF 2.0 settings dictionary describing activation, deactivation and initial artwork state. It is unique to each annotation. If absent, the first configuration is loaded.':
        'Dictionnaire PDF 2.0 optionnel décrivant l’activation, la désactivation et l’état initial du contenu multimédia. Il est propre à chaque annotation. En son absence, la première configuration est chargée.',
    'Optional indirect reference to a RichMediaConfiguration dictionary present in the Configurations array of the RichMediaContent dictionary specified by this annotation. Defaults to the first configuration in that array.':
        'Référence indirecte optionnelle vers un dictionnaire RichMediaConfiguration présent dans le tableau Configurations du RichMediaContent de cette annotation. Par défaut, la première configuration de ce tableau est utilisée.',
    'Optional array of indirect file-specification dictionary references describing JavaScript files present in the RichMediaContent Assets name tree. Empty or absent means no script is executed.':
        'Tableau optionnel de références indirectes vers des spécifications de fichiers JavaScript présentes dans l’arbre de noms Assets du RichMediaContent. Une entrée vide ou absente n’exécute aucun script.',
    'Required nonempty array of indirect references to RichMediaConfiguration dictionaries.':
        'Tableau obligatoire et non vide de références indirectes vers des dictionnaires RichMediaConfiguration.',
    'Required indirect reference to the instance asset file specification. The asset may also occur in the RichMediaContent Assets name tree; the primary instance asset is not required to have a name-tree entry. Other assets referenced by name must be available in that name tree.':
        'Référence indirecte obligatoire vers la spécification du fichier principal de l’instance. Ce fichier peut aussi figurer dans l’arbre Assets du RichMediaContent, sans obligation d’y être nommé. Les autres ressources désignées par leur nom doivent figurer dans cet arbre.',
    '(Optional; deprecated in PDF 2.0) The current revision number of this structure element (see 14.7.6.3, "Attribute revision numbers"). The value shall be a non-negative integer. Default value: 0.':
        '(Optionnel ; déprécié en PDF 2.0) Numéro de révision actuel de l’élément de structure (14.7.6.3), sous forme d’entier positif ou nul. Valeur par défaut : 0.',
    'Optional inheritable vertical glyph orientation: /Auto or an integer multiple of 90 degrees from -180 through 360. Default: /Auto. This affects glyph alignment and width as specified in Table 380.':
        'Orientation verticale optionnelle et héritable des glyphes : /Auto ou un entier multiple de 90 degrés compris entre -180 et 360. Défaut : /Auto. Elle influence l’alignement et la largeur des glyphes selon le tableau 380.',
    '(Optional; not inheritable; PDF 2.0) A flag specifying whether the list is a continuation of a previous list in the structure tree (true), or not (false). Default value: false. If the ContinuedFrom attribute is not present, the continuation is from the preceding list at the same level in the structure hierarchy.':
        '(Optionnel ; non héritable ; PDF 2.0) Indique si cette liste poursuit une liste précédente de l’arbre de structure (true) ou non (false). Valeur par défaut : false. Sans ContinuedFrom, la continuation concerne la liste précédente de même niveau dans la hiérarchie.',
    '(Optional; not inheritable; PDF 2.0) The ID (see “Table 355 — Entries in a structure element dictionary") of the list for which this list is a continuation.':
        '(Optionnel ; non héritable ; PDF 2.0) ID de la liste dont celle-ci est la continuation, selon le tableau 355.',
    '(Optional; not inheritable; PDF 2.0) The type of artifact that this attribute describes; if present, shall be one of the names Pagination, Layout, Page or Inline (PDF 2.0). • Pagination artifacts are ancillary page features such as running heads or folios (page numbers) • Layout artifacts are purely cosmetic typographical or design elements such as footnote rules or decorative ornaments • Page artifacts are production aids extraneous to the document itself, such as cut marks and print control patches • Inline artifacts enclose artifact content that has context in the document’s logical structure, typically, artifacts of subtype LineNum or Redaction NOTE Inline artifacts can be used to provide context in the logical structure to any artifact. This is similar to an inline structure element.':
        '(Optionnel ; non héritable ; PDF 2.0) Type d’artefact, parmi Pagination, Layout, Page ou Inline (PDF 2.0). Pagination désigne les éléments annexes comme les titres courants et numéros de page ; Layout les ornements typographiques ou graphiques ; Page les aides de production comme les traits de coupe et plages de contrôle ; Inline un contenu d’artefact ayant un contexte dans la structure logique, généralement LineNum ou Redaction. NOTE Inline peut donner un contexte logique à tout artefact, comme un élément de structure en ligne.',
    '(Optional; not inheritable; PDF 2.0) An array of four numbers in default user space units giving the coordinates of the left, bottom, right, and top edges, respectively, of the artifact’s bounding box (the rectangle that completely encloses its visible extent).':
        '(Optionnel ; non héritable ; PDF 2.0) Tableau de quatre nombres, dans l’espace utilisateur par défaut, donnant les bords gauche, inférieur, droit et supérieur du rectangle englobant toute la partie visible de l’artefact.',
    '(Optional; not inheritable; PDF 2.0) The subtype of the artifact. This entry should appear only when the Type entry has a value of Pagination or Inline. Valid values are Header, Footer, Watermark, PageNum (PDF 2.0), Bates (PDF 2.0), LineNum (PDF 2.0) and Redaction (PDF 2.0). Additional values may be specified for this entry, provided they comply with the naming conventions described in Annex E, "Extending PDF".':
        '(Optionnel ; non héritable ; PDF 2.0) Sous-type d’artefact, qui devrait apparaître uniquement pour Type=Pagination ou Inline. Valeurs valides : Header, Footer, Watermark, PageNum (PDF 2.0), Bates (PDF 2.0), LineNum (PDF 2.0) et Redaction (PDF 2.0). Des valeurs supplémentaires peuvent être définies conformément aux conventions de nommage de l’annexe E.',
    '(Shall not be present if Start is present; PDF 2.0) EC3 issue 612: a nonempty flat array of indirect references to immediate descendant DPart dictionaries. Nested arrays are not permitted.':
        '(Interdit si Start est présent ; PDF 2.0) EC3 #612 : tableau plat et non vide de références indirectes vers les dictionnaires DPart enfants immédiats. Les tableaux imbriqués sont interdits.',
    'EC3 issue 290 prohibits Metadata in DPart dictionaries. This original table entry is retained for source traceability; the executable DPart constraint rejects a non-null value. Hierarchy XMP belongs on DPartRoot.':
        'EC3 #290 interdit Metadata dans les dictionnaires DPart. L’entrée du tableau original est conservée pour la traçabilité ; la contrainte DPart exécutable rejette toute valeur non nulle. Les métadonnées XMP de la hiérarchie appartiennent à DPartRoot.',
})

ISO2_DESCRIPTIONS_FR.update({
    'Historical Web Capture identifier name tree; deprecated in PDF 2.0.':
        'Arbre de noms des identifiants Web Capture historiques ; déprécié en PDF 2.0.',
    'Historical Web Capture URL name tree; deprecated in PDF 2.0.':
        'Arbre de noms des URL Web Capture historiques ; déprécié en PDF 2.0.',
    'An optional array of 3D node dictionaries; its applicability does not require NR to be present.':
        'Tableau optionnel de dictionnaires de nœuds 3D ; son application n’exige pas la présence de NR.',
    'A nonempty array of embedded file-specification dictionaries or URL file-specification dictionaries with FS equal to URL and F a PDFDocEncoded text string limited to RFC3986 characters.':
        'Tableau non vide de dictionnaires de spécification de fichiers incorporés ou de fichiers URL, avec FS égal à URL et F une chaîne texte en PDFDocEncoding limitée aux caractères RFC3986.',
    'An ASCII string identifying the type of data in D; it shall conform to the RFC2045 content-type specification.':
        'Chaîne ASCII identifiant le type des données de D ; elle doit respecter la spécification content-type de la RFC2045.',
    'The indirect page reference for the marked-content sequence takes precedence over the containing structure element Pg and is required when that structure element has no Pg.':
        'La référence indirecte à la page de la séquence de contenu marqué prend priorité sur Pg de l’élément de structure parent ; elle est obligatoire lorsque ce parent n’a pas de Pg.',
    'The indirect page reference for the object takes precedence over the containing structure element Pg and is required when that structure element has no Pg.':
        'La référence indirecte à la page de l’objet prend priorité sur Pg de l’élément de structure parent ; elle est obligatoire lorsque ce parent n’a pas de Pg.',
})


def iso2_description(value, language):
    if language == 'fr' and value in ISO2_DESCRIPTIONS_FR:
        return ISO2_DESCRIPTIONS_FR[value], 'fr'
    # Original normative excerpts remain English. Complete site builds require
    # French translations for every project-authored summary.
    return value, 'en'


def route_for(route, language):
    # Generated example documents are shared artifacts, including HTML outputs.
    if route.startswith('examples/') or not route.endswith('.html'):
        return route
    if language == 'fr':
        return 'fr/' + route
    return ENGLISH_ROUTES.get(route, route)


def localized_source(owner, source, language):
    if owner == 'documentation':
        return source.replace('docs/', 'docs/en/', 1) if language == 'en' else source
    if language == 'fr':
        if source in {'README.md', 'SECURITY.md', 'CHANGELOG.md'}:
            return source.replace('.md', '.fr.md')
        return source.replace('docs/', 'docs/fr/', 1)
    return source


def canonical_source(owner, source):
    if owner == 'documentation':
        return source.replace('docs/en/', 'docs/', 1).replace('.fr.md', '.md')
    return source.replace('docs/fr/', 'docs/', 1).replace('.fr.md', '.md')


TEXT = {
    'Galerie et démo HTML': 'HTML gallery and demo',
    'Dérivation HTML': 'HTML derivation',
    'Démo HTML': 'HTML demo',
    'Explorer les exemples et essayer la conversion locale →': 'Explore examples and try local conversion →',
    'Dériver du HTML depuis un PDF': 'Derive HTML from PDF',
    'Dériver du HTML depuis un PDF balisé': 'Derive HTML from tagged PDF',
    'Structure logique, contenu Unicode et HTML sémantique avec diagnostics explicites.': 'Logical structure, Unicode content and semantic HTML with explicit diagnostics.',
    'Architecture de la dérivation HTML': 'HTML derivation architecture',
    'Couverture de la dérivation HTML': 'HTML derivation coverage',
    'Exigences de la dérivation HTML': 'HTML derivation requirements',
    'Politiques de dérivation HTML': 'HTML derivation policies',
    'Graphiques PDF et rendu de figures': 'PDF graphics and figure rendering',
    'Couleurs et transparence des images décodées': 'Decoded image colour and transparency',
    'Validation des signatures PDF': 'PDF signature validation',
    'Sécurité du HTML dérivé': 'Derived HTML security',
    'Référence Deriving HTML from PDF': 'Deriving HTML from PDF reference',
    'Module optionnel : dérivation HTML': 'Optional module: HTML derivation',
    'Résultat HTML': 'HTML result',
    'Télécharger le HTML': 'Download the HTML',
    'Lire la source HTML': 'Read the HTML source',
    'Ce PDF balisé est l’entrée de la conversion. Le résultat HTML est produit par le script exécuté pendant la construction du site ; l’aperçu conserve la structure sémantique plutôt que la mise en page du PDF.': 'This tagged PDF is the conversion input. The HTML result is produced by the script run during the site build; its preview preserves semantic structure rather than the PDF layout.',
    'Sortie réelle de la dérivation, isolée dans une frame sans autorisation de script, de formulaire ou de navigation de la page principale.': 'Actual derivation output, isolated in a frame without permission to run scripts, submit forms or navigate the parent page.',
    'Bundle PDF 2.0 : mécanismes et vérifications': 'PDF 2.0 bundle: mechanisms and validation',
    'Spécifications complémentaires PDF 2.0': 'PDF 2.0 companion specifications',
    'Métadonnées, déclarations et parties documentaires': 'Metadata, declarations and document parts',
    'XMP, portée des déclarations, compensation du point noir et DPart.': 'XMP, declaration scope, black point compensation and DPart.',
    'Une enveloppe pour un PDF chiffré': 'A wrapper for an encrypted PDF',
    'Collection masquée, fichier associé EncryptedPayload et protection du contenu.': 'Hidden collection, EncryptedPayload associated file and content protection.',
    'Espaces de noms et PDF bien balisé': 'Namespaces and well-tagged PDF',
    'Rôles qualifiés, règles d’inclusion et rapport de vérification WTPDF.': 'Qualified roles, inclusion rules and WTPDF audit report.',
    'Algorithmes modernes et intégrité PDF': 'Modern algorithms and PDF integrity',
    'Signature SHA-3, AES-GCM et MAC vérifiés indépendamment.': 'Independently verified SHA-3 signatures, AES-GCM and PDF MAC.',
    'Couverture des éditions PDF': 'Coverage by PDF edition',
    'Règles de source et corrections vérifiées': 'Source rules and reviewed corrections',
    'Appliquer une caviardisation': 'Apply redaction',
    'Révisions natives protégées': 'Protected native revisions',
    'Remplir un formulaire certifié': 'Fill a certified form',
    'DocMDP, FieldMDP et remplacement isolé de l’apparence à texte variable.': 'DocMDP, FieldMDP and isolated variable-text appearance replacement.',
    'Suppression conservatrice des données et écriture d’un nouveau fichier.': 'Conservative data removal and writing a fresh file.',
    'Authentification des PDF chiffrés': 'Encrypted PDF authentication',
    'Authentification par clé publique': 'Public-key authentication',
    'Authentifier le MAC du PDF source': 'Authenticate the source PDF MAC',
    'Positionnement et variations OpenType': 'OpenType positioning and variations',
    'PDF 2.0 : objets et mécanismes': 'PDF 2.0: objects and mechanisms',
    'Horodatages et preuves de validation': 'Timestamps and validation evidence',
    'RFC3161, révisions signées, DSS et VRI explicites.': 'RFC3161, signed revisions, explicit DSS and VRI.',
    'Objets géospatiaux et mesures': 'Geospatial objects and measurements',
    'Systèmes de coordonnées, points appariés, viewports et nuages de points.': 'Coordinate systems, paired points, viewports and point clouds.',
    'Destinations vers la structure logique': 'Destinations targeting logical structure',
    'Cibles sémantiques, parcours du contenu et destinations de page de repli.': 'Semantic targets, content traversal and fallback page destinations.',
    'PHP 8.3+ 64 bits · PDF 1.7 et 2.0': '64-bit PHP 8.3+ · PDF 1.7 and 2.0',
    'PDF 2.0 et fichiers associés': 'PDF 2.0 and associated files',
    'Métadonnées UTF-8, fichiers AF et propriétés MCAF nommées.': 'UTF-8 metadata, AF files and named MCAF properties.',
    'PDF 2.0 : ISO 32000-2': 'PDF 2.0: ISO 32000-2',
    'Original conservé dans le dépôt du core. Inventaire des tableaux et contrôles sémantiques restent distincts.': 'Original retained in the core repository. Table inventory and semantic validation remain distinct.',
    'Extrait normatif original en anglais.': 'Original normative excerpt in English.',
    'Définitions communes :': 'Common definitions:',
    'Clé fournie explicitement': 'Explicitly supplied key',
    'Éléments indirects dans le tableau': 'Indirect array elements required',
    'Premiers mécanismes PDF 2.0': 'First PDF 2.0 mechanisms',
    'PHP 8.3+ · PDF 1.7 · Premiers mécanismes PDF 2.0': 'PHP 8.3+ · PDF 1.7 · First PDF 2.0 mechanisms',
    'Requis': 'Required', 'Facultatif': 'Optional',
    'Définition ISO 32000-2:2020 EC3': 'ISO 32000-2:2020 EC3 definition',
    'Métadonnées de la source au commit documenté ↗': 'Source metadata at the documented commit ↗',
    'Errata publics ↗': 'Public errata ↗',
    'Original conservé dans le dépôt du core. Catalogue pilote — couverture complète en attente.': 'Original retained in the core repository. Pilot catalogue — complete coverage pending.',
    'Original PDF au commit documenté ↗': 'Original PDF at the documented commit ↗',
    'Page PDF physique': 'Physical PDF page',
    'Correction EC3': 'EC3 correction',
    'Résumé d’implémentation rédigé pour le projet.': 'Project-authored implementation summary.',
    'Périmètre et limites PDF 2.0.': 'PDF 2.0 scope and limits.',
    'Guides': 'Guides', 'Tutoriels': 'Tutorials', 'Recettes': 'Recipes',
    'Couverture des deux références': 'Coverage of both references',
    'Supplément Adobe et extensions': 'Adobe supplement and extensions',
    'Références Adobe conservées': 'Preserved Adobe references',
    'Démarrer': 'Getting started', 'Comprendre les composants': 'Understanding the components',
    'Core et modules optionnels': 'Core and optional modules',
    'Historique physique des révisions': 'Physical revision history',
    'Politique structurelle PDF 2.0': 'PDF 2.0 structural policy',
    'Axes des fontes variables': 'Variable font axes',
    'Noms et métadonnées OS/2': 'Names and OS/2 metadata',
    'Métriques verticales et variables': 'Vertical and variable metrics',
    'Contours TrueType': 'TrueType outlines',
    'Contours CFF et CFF2': 'CFF and CFF2 outlines',
    'Variations des contours TrueType': 'TrueType outline variations',
    'En-têtes et styles des fontes': 'Font headers and styles',
    'Métriques pré-calculées': 'Precomputed device metrics',
    'Migration vers le core 0.12': 'Migrating to core 0.12',
    'Migration vers le core 0.11': 'Migrating to core 0.11',
    'Migration vers le core 0.5': 'Migrating to core 0.5',
    'Migration vers le core 0.4': 'Migrating to core 0.4',
    'Couverture de la norme': 'Specification coverage', 'Sécurité': 'Security',
    'Signaler une vulnérabilité': 'Reporting a vulnerability',
    'Versions et changements': 'Releases and changes', 'Parcours des tutoriels': 'Tutorial learning path',
    'Recettes pratiques': 'Practical recipes', 'Un tableau explicite': 'An explicit table',
    'Premier document': 'First document', 'Pages et texte': 'Pages and text',
    'Dessin et transformations': 'Drawing and transformations', 'Signets et destinations': 'Bookmarks and destinations',
    'Liens cliquables': 'Clickable links', 'Dégradé et fonction': 'Gradient and function',
    'Objets compressés': 'Compressed objects', 'Police TrueType et Unicode': 'TrueType font and Unicode',
    'Images JPEG et PNG': 'JPEG and PNG images', 'Révisions incrémentales': 'Incremental revisions',
    'Lire les pages d’un PDF externe': 'Reading pages from an external PDF',
    'Extensions Adobe et numérotation Bates': 'Adobe extensions and Bates numbering',
    'Champs et apparences AcroForm': 'AcroForm fields and appearances',
    'Structure logique et contenu balisé': 'Logical structure and tagged content',
    'Linéarisation': 'Linearization', 'Couleurs, motifs et dégradés': 'Colours, patterns and gradients',
    'CMaps et Unicode': 'CMaps and Unicode', 'Filtres et prédicteurs': 'Filters and predictors',
    'Signatures PDF': 'PDF signatures', 'Images, transparence et calques': 'Images, transparency and layers',
    'Fontes natives et écriture verticale': 'Native fonts and vertical writing',
    'Navigation, articles et présentation': 'Navigation, articles and presentation',
    'Fichiers incorporés et collections': 'Embedded files and collections',
    'Suppression et générations': 'Deletion and generations', 'Politique du champ signé': 'Signature field policy',
    'Police, contenu, page et catalogue.': 'Font, content, page and catalog.',
    'Ressources partagées, héritage et lignes explicites.': 'Shared resources, inheritance and explicit lines.',
    'Chemins, couleurs, courbes et matrices.': 'Paths, colours, curves and matrices.',
    'Un plan hiérarchique et des destinations nommées.': 'A hierarchical outline and named destinations.',
    'Annotations internes et actions URI.': 'Internal annotations and URI actions.',
    'Un motif RGB en XObject et en image inline.': 'An RGB pattern as an XObject and an inline image.',
    'Une fonction de type 2 alimente un shading axial.': 'A type 2 function drives axial shading.',
    'Filtres, flux d’objets et références croisées.': 'Filters, object streams and cross-references.',
    'Programme incorporé, CID, métriques et correspondance Unicode.': 'Embedded program, CID, metrics and Unicode mapping.',
    'Fichiers image, couleurs, échantillons et transparence.': 'Image files, colours, samples and transparency.',
    'Octets conservés, remplacements explicites et chaînage des xref.': 'Preserved bytes, explicit replacements and chained cross-references.',
    'Arbre vérifié, attributs hérités et flux décodés explicitement.': 'Validated tree, inherited attributes and explicitly decoded streams.',
    'Déclaration des extensions, artefacts et numéros documentaires.': 'Extension declarations, artifacts and document numbering.',
    'Arbres de champs, widgets, valeurs et apparences.': 'Field trees, widgets, values and appearances.',
    'Ordre de lecture, MCID, ParentTree et liens vers les annotations.': 'Reading order, MCID, ParentTree and annotation links.',
    'Ordre physique des objets, dépendances et indices binaires.': 'Physical object order, dependencies and binary hints.',
    'Espaces couleur, cellules répétées et sept types de shading.': 'Colour spaces, repeated cells and seven shading types.',
    'Encodage composé, CID, UseCMap et extraction Unicode.': 'Composite encoding, CID, UseCMap and Unicode extraction.',
    'LZW et prédiction TIFF/PNG des lignes avant compression.': 'LZW and TIFF/PNG row prediction before compression.',
    'Réservation Contents, ByteRange et signature CMS explicite.': 'Reserved Contents, ByteRange and an explicit CMS signature.',
    'Profondeurs, masques, groupes, ExtGState et contenu optionnel.': 'Bit depths, masks, groups, ExtGState and optional content.',
    'Type3, fontes simples, programmes PDF et métriques verticales.': 'Type3, simple fonts, PDF programs and vertical metrics.',
    'Labels, cadrages, anneaux de lecture et séquences.': 'Labels, viewports, article rings and sequences.',
    'Octets, métadonnées, EF/RF/CI et présentation de collection.': 'Bytes, metadata, EF/RF/CI and collection presentation.',
    'Liste libre, réutilisation et identités historiques.': 'Free list, reuse and historical identities.',
    'Seeds, verrou, apparence et preuve du résultat effectivement signé.': 'Seed values, lock, appearance and evidence of the actual signed result.',
    'Objets et références': 'Objects and references', 'Écriture et fichier': 'Writing and file structure',
    'Contenu, texte et graphisme': 'Content, text and graphics', 'Structure documentaire': 'Document structure',
    'Fonctions PDF': 'PDF functions', 'Filtres': 'Filters', 'Conventions lexicales': 'Lexical conventions',
    'Modèle de norme': 'Specification model', 'Dictionnaires normalisés': 'Standard dictionaries',
    'Entrées normalisées': 'Standard entries', 'Définitions normalisées': 'Standard definitions',
    'Extensions Adobe : dictionnaires, entrées et définitions': 'Adobe extensions: dictionaries, entries and definitions',
    'Chiffrement, certificats et signatures': 'Encryption, certificates and signatures',
    'Module optionnel : fontes externes': 'Optional module: external fonts',
    'Module optionnel : images externes': 'Optional module: external images',
    'Module optionnel : lecture de PDF': 'Optional module: PDF reading',
    'Modèle objet OpenType indépendant': 'Independent OpenType object model',
    'Architecture OpenType': 'OpenType architecture',
    'Contrats des codecs d’image': 'Image codec contracts',
    'Moteurs natifs et codecs PHP': 'Native engines and PHP codecs',
    'Résolution explicite des flux externes': 'Explicit external stream resolution',
    'Décodage et délimitation CCITT': 'CCITT decoding and framing',
    'Importer les objets lus': 'Importing parsed objects',
    'Déclarations de couleur PNG': 'PNG colour declarations',
    'Mise en page OpenType dans les PDF': 'OpenType layout in PDF',
    'Collections et paramètres OpenType': 'OpenType collections and parameters',
    'Codecs d’image PHP indépendants': 'Independent PHP image codecs',
    'Décoder les images en PHP': 'Decode images in PHP',
    'Décodage JPEG': 'JPEG decoding',
    'Décodage JPEG 2000': 'JPEG 2000 decoding',
    'Décodage JBIG2': 'JBIG2 decoding',
    'Couverture OpenType': 'OpenType coverage',
    'Substitutions de glyphes': 'Glyph substitutions',
    'Lire un PDF': 'Reading a PDF', 'Architecture du lecteur': 'Reader architecture',
    'Pages, héritage et flux': 'Pages, inheritance and streams', 'Composants du lecteur': 'Reader components',
    'Limites et sécurité du lecteur': 'Reader limits and security', 'Convertir des images': 'Converting images',
    'Contrats des convertisseurs d’images': 'Image converter contracts', 'Analyser des fontes': 'Inspecting fonts',
    'Du programme TrueType aux objets PDF': 'From a TrueType program to PDF objects',
    'Découvrir': 'Discover', 'Accueil': 'Home', 'Core et modules': 'Core and modules',
    'Les composants': 'Components', 'Core : objets et écriture': 'Core: objects and writing',
    'Apprendre': 'Learn', 'Tous les tutoriels': 'All tutorials', 'Recette : tableau': 'Recipe: table',
    'Explorer': 'Explore', 'Référence des composants': 'Component reference', 'Supplément Adobe': 'Adobe supplement',
    'Versions': 'Releases', 'Sur cette page': 'On this page', 'Aller au contenu': 'Skip to content',
    'objet par objet': 'object by object', 'Navigation principale': 'Main navigation', 'Référence': 'Reference',
    'Le catalogue relie l’arbre des pages, les contenus et les ressources': 'The catalog connects the page tree, content and resources',
    'PDF d’entrée': 'Input PDF', 'Résultat PDF': 'PDF result', 'Voir le PDF d’entrée': 'View the input PDF',
    'Voir le résultat PDF': 'View the PDF result',
    'Ce PDF est l’entrée du lecteur : une fixture originale créée avec pypdf et qpdf, indépendamment du writer PHP. Ses trois pages sont reproduites ci-dessous ; le résultat de la lecture figure ensuite dans la sortie console.': 'This PDF is the reader input: an original fixture created with pypdf and qpdf, independently of the PHP writer. All three pages appear below, followed by the reader output.',
    'Ce fichier a été généré avec le code de cette documentation. Toutes ses pages sont reproduites ci-dessous ; ouvrir le PDF pour utiliser ses liens et ses signets.': 'This file was generated with the code in this documentation. All pages appear below; open the PDF to use its links and bookmarks.',
    'Code de': 'Code from', 'Consulter la source au commit documenté ↗': 'View the source at the documented commit ↗',
    'Origine du PDF d’entrée ↗': 'Input PDF source ↗', 'Résultat de la lecture': 'Reader output',
    'Sortie réelle du script exécuté sur le PDF d’entrée pendant la construction de cette documentation.': 'Actual script output from reading the input PDF while building this documentation.',
    'Télécharger la sortie console': 'Download the console output', 'Ouvrir le PDF ↗': 'Open the PDF ↗',
    'Télécharger': 'Download', 'Télécharger le code PHP': 'Download the PHP code',
    'Utiliser le lecteur PDF du navigateur': 'Use the browser PDF viewer',
    'Ce lecteur dépend du navigateur. Si le document ne s’affiche pas, utiliser « Ouvrir le PDF » ou « Télécharger ».': 'This viewer depends on your browser. If the document does not appear, use “Open the PDF” or “Download”.',
    'Code source complet': 'Complete source code', 'Code source': 'Source code', 'Lire et voir le PDF →': 'Read and view the PDF →',
    'Rechercher un composant': 'Search for a component', 'Type de composant': 'Component type', 'Tous les types': 'All types',
    'Installer avec Composer · Packagist ↗': 'Install with Composer · Packagist ↗',
    'Guide du package →': 'Package guide →', 'Référence API →': 'API reference →',
    'Présentation': 'Overview', 'Référence API': 'API reference', 'Signalements privés': 'Private reports',
    'Guides du module': 'Module guides', 'Installer le core': 'Install the core',
    'Le core représente les objets et mécanismes de PDF 1.7 et PDF 2.0 et les compose en fichiers PDF. Il fournit la syntaxe, les dictionnaires, les flux, les pages, les images et les polices PDF, ainsi que l’écriture et les révisions. Les lecteurs de PDF externes, PNG/JPEG et TrueType sont des modules optionnels.': 'The core represents PDF 1.7 and PDF 2.0 objects and mechanisms and assembles them into PDF files. It provides syntax, dictionaries, streams, pages, PDF images and fonts, writing and revisions. External PDF, PNG/JPEG and TrueType readers are optional modules.',
    'Composer installe uniquement le core et vérifie ses extensions PHP requises. Les modules optionnels sont choisis par l’application.': 'Composer installs the core and checks its required PHP extensions. The application chooses which optional modules to install.',
    'Commencer et construire': 'Get started and build', 'Installation et premier document': 'Installation and first document',
    'Tutoriels avec code et PDF': 'Tutorials with code and PDFs', 'Responsabilités des composants': 'Component responsibilities',
    'Référence et versions': 'Reference and releases', 'API du core': 'Core API',
    'Définitions et couverture de la norme': 'Definitions and specification coverage',
    'Mécanismes vérifiés et limites': 'Verified mechanisms and limits', 'Sécurité et responsabilités': 'Security and responsibilities',
    'Core : objets PDF et écriture': 'Core: PDF objects and writing',
    'Le format PDF.': 'The PDF format.', 'Objet par objet.': 'Object by object.',
    'Comprendre les structures, composer les objets, maîtriser les octets. Une documentation pour explorer le format et construire vos propres fichiers PDF.': 'Understand structures, compose objects and control the bytes. Explore the format and build your own PDF files.',
    'Créer mon premier PDF →': 'Create my first PDF →', 'Explorer les composants': 'Explore the components',
    'Du catalogue à la page': 'From catalog to page', '01 / point d’entrée': '01 / entry point',
    '02 / arbre du document': '02 / document tree', '03 / contenu & ressources': '03 / content & resources',
    'composants documentés': 'documented components', 'dictionnaires ISO et Adobe': 'ISO and Adobe dictionaries',
    'exemples PDF à explorer': 'PDF examples to explore', 'tokens d’opérateurs PDF': 'PDF operator tokens',
    'Apprendre avec les objets': 'Learn with objects', 'Construire un document et explorer ses pages': 'Build a document and explore its pages',
    'Chaque tutoriel relie les explications aux objets PHP et au PDF créé ou lu. Consultez ses pages, le script et le résultat de son exécution.': 'Each tutorial connects the explanations to PHP objects and the PDF being created or read. Explore its pages, script and execution result.',
    'Un core PDF, des modules au choix': 'A PDF core, optional modules',
    'Le core représente les objets et les mécanismes de la norme Adobe. Les modules de lecture PDF et de conversion d’images ou de fontes dépendent du core. Les modèles OpenType et de codecs PHP sont indépendants et s’installent sans aucun package PDF.': 'The core represents the objects and mechanisms in the Adobe specification. PDF reading and image or font conversion modules depend on the core. The OpenType and PHP codec models are independent and install without any PDF package.',
    'Choisir les packages et comprendre leur frontière →': 'Choose packages and understand their scope →',
    'Trois chemins pour explorer le projet': 'Three ways to explore the project', 'Comprendre les responsabilités': 'Understand responsibilities',
    'Valeurs, graphes, ressources, fonctions et écriture : comment les familles se composent.': 'Values, graphs, resources, functions and writing: how the component families fit together.',
    'Consulter la référence': 'Browse the reference',
    'Les signatures et l’héritage de chaque composant, avec les sources et les tableaux de la norme.': 'Signatures and inheritance for every component, with source code and specification tables.',
    'Assembler un exemple pratique': 'Assemble a practical example',
    'Un tableau explicite : cellules, couleurs, grille et positionnement du texte.': 'An explicit table: cells, colours, grid and text positioning.',
    'Les signatures, exemples et guides des modules proviennent de ces versions publiées, fixées à leurs commits exacts. La couverture et les traitements restant à implémenter sont détaillés dans': 'Signatures, examples and module guides come from these published releases, pinned to their exact commits. Coverage and remaining mechanisms are detailed in',
    'la couverture de la norme': 'specification coverage', 'Le format PDF, objet par objet': 'The PDF format, object by object',
    'Définition dans la norme': 'Definition in the specification', 'Référence indirecte exigée': 'Indirect reference required',
    'Objet direct exigé': 'Direct object required', 'Éléments directs dans le tableau': 'Direct array elements required',
    'Qualificateur :': 'Qualifier:', 'Non précisé': 'Unspecified', 'Entrée': 'Entry', 'Type PDF': 'PDF type',
    'Exigence de la source': 'Source requirement', 'Tableau': 'Table',
    'Les descriptions conditionnelles restent traçables. La présence d’une définition ne réalise pas à elle seule un codec, une signature ou tous les traitements du format.': 'Conditional descriptions remain traceable. A definition alone does not implement a codec, a signature or every format mechanism.',
    'Lire la couverture.': 'Read the coverage.', 'Définition dans le supplément Adobe': 'Definition in the Adobe supplement',
    'Définition dans la norme ISO': 'Definition in the ISO specification', 'Exigence': 'Requirement',
    'Chaque entrée conserve sa source ISO ou Adobe. Les règles et traitements associés figurent dans': 'Each entry preserves its ISO or Adobe source. Related rules and mechanisms are described in',
    'la couverture du supplément': 'supplement coverage', 'Déclarée par': 'Declared by', 'Voir le code ↗': 'View the code ↗',
    'Lire la déclaration source ↗': 'Read the source declaration ↗', 'Ce composant appartient à': 'This component belongs to',
    ', un module installé séparément du core.': ', a module installed separately from the core.',
    'Guide du module.': 'Module guide.', 'API du package.': 'Package API.',
    'Héritage et contrats': 'Inheritance and contracts', 'Ce type ne déclare pas de parent, d’interface ou de trait.': 'This type declares no parent, interface or trait.',
    'Méthodes déclarées': 'Declared methods', 'Méthodes héritées': 'Inherited methods', 'Propriétés': 'Properties',
    'Déclaration': 'Declaration', 'Provenance et documentation': 'Origin and documentation',
    'Constantes': 'Constants', 'Nom': 'Name', 'Valeur PHP': 'PHP value', 'Provenance': 'Origin',
    'Cas de l’enum': 'Enum cases', 'Héritage': 'Inheritance', 'Norme': 'Specification', 'Méthodes': 'Methods',
    'Lire le guide du package →': 'Read the package guide →', 'Référence par package': 'Reference by package',
    'Chaque classe, interface, enum et trait du core et des modules installés pour cette documentation possède une fiche. Les composants optionnels portent leur nom de package ; les installer dépend des traitements nécessaires à votre application. Les signatures sont extraites par Reflection ; les descriptions normalisées proviennent du catalogue de la référence PDF.': 'Every class, interface, enum and trait in the core and documented modules has a reference page. Optional components show their package name; install them according to your application’s needs. Signatures are extracted through Reflection; standard descriptions come from the PDF reference catalogue.',
    'Explorer par package': 'Explore by package', 'Explorer par famille': 'Explore by family', 'Consulter la famille →': 'Browse the family →',
    'Les composants de cette famille sont tous accessibles ci-dessous. La recherche globale permet aussi de retrouver une entrée PDF ou un nom de type.': 'All components in this family are available below. Global search also finds PDF entries and type names.',
    'Repères pour commencer': 'Starting points', 'Tous les composants': 'All components',
    'Source de ce guide au commit documenté ↗': 'Guide source at the documented commit ↗',
    'Page introuvable': 'Page not found', 'Cette adresse ne correspond pas à une page publiée.': 'This address does not match a published page.',
    'ou': 'or', 'revenir à l’accueil': 'return home',
}

# Variable interface messages have bounded, explicit sentence templates.
PATTERNS = [
    (r'Correction EC3 /(.+)', lambda m: 'EC3 correction /' + m[1]),
    (r'§(.+) · page PDF (\d+)', lambda m: '§' + m[1] + ' · PDF page ' + m[2]),
    (r'(Requis|Facultatif); conditionnel', lambda m: translate(m[1]) + '; conditional'),
    (r'(\d{2})\. (.+)', lambda m: m[1] + '. ' + translate(m[2])),
    (r'Tutoriel (\d{2})', lambda m: 'Tutorial ' + m[1]),
    (r'Aperçu : (.+)', lambda m: 'Preview: ' + translate(m[1])),
    (r'(\d[\d\u202f,]*) composants', lambda m: m[1] + ' components'),
    (r'(\d[\d\u202f,]*) composants dans le code, dont les définitions et entrées normalisées\.', lambda m: m[1] + ' components in the code, including standard definitions and entries.'),
    (r'Module optionnel(.*)', lambda m: 'Optional module' + m[1]),
    (r'Optionnel · (.+)', lambda m: 'Optional · ' + m[1]),
    (r'Version publiée (.+)', lambda m: 'Published release ' + m[1]),
    (r'API de (.+)', lambda m: 'API for ' + m[1]),
    (r'Nom fixe /(.+)', lambda m: 'Fixed name /' + m[1]),
    (r'Noms permis : (.+)', lambda m: 'Allowed names: ' + m[1]),
    (r'Longueur exacte du tableau : (\d+)', lambda m: 'Exact array length: ' + m[1]),
    (r'Tableau (.+)', lambda m: 'Table ' + m[1]),
    (r'page PDF (\d+) ↗', lambda m: 'PDF page ' + m[1] + ' ↗'),
    (r'Correction d’implémentation /(.+)', lambda m: 'Implementation correction /' + m[1]),
    (r'(\d+) types dérivés directement', lambda m: m[1] + ' directly derived types'),
    (r'(\d+) méthodes des parents et contrats', lambda m: m[1] + ' methods from parents and contracts'),
    (r'Agrandir la page (\d+) sur (\d+)', lambda m: 'Enlarge page ' + m[1] + ' of ' + m[2]),
    (r'Page (\d+) sur (\d+)', lambda m: 'Page ' + m[1] + ' of ' + m[2]),
    (r'(PDF d’entrée|Résultat PDF) (.+) : page (\d+) sur (\d+)', lambda m: translate(m[1]) + ' ' + m[2] + ': page ' + m[3] + ' of ' + m[4]),
    (r'(PDF d’entrée|Résultat PDF) : (.+)', lambda m: translate(m[1]) + ': ' + m[2]),
    (r'Aperçu des (\d+) pages du PDF (.+)', lambda m: 'Preview of all ' + m[1] + ' pages in PDF ' + m[2]),
    (r'Lire le script commenté : (.+)', lambda m: 'Read the commented script: ' + m[1]),
    (r'(.+) — modèle objet PDF pour PHP 8\.3\+\.', lambda m: translate(m[1]) + ' — PDF object model for PHP 8.3+.'),
    (r'(.+) · PDFToolkit', lambda m: translate(m[1]) + ' · PDFToolkit'),
]


def translate(value):
    stripped = value.strip()
    result = TEXT.get(stripped)
    if result is None:
        for pattern, replacement in PATTERNS:
            match = re.fullmatch(pattern, stripped)
            if match:
                result = replacement(match)
                break
    return value if result is None else value[:len(value) - len(value.lstrip())] + result + value[len(value.rstrip()):]


class InterfaceTranslator(HTMLParser):
    """Translate explicit presentation strings without changing markup or code."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        if tag in {'code', 'pre', 'script', 'style'}:
            self.protected.append(tag)
        rendered = []
        for key, value in attrs:
            if value is None:
                rendered.append(key)
            else:
                if key in {'alt', 'title', 'aria-label'} or tag == 'meta' and key == 'content' and dict(attrs).get('name') == 'description':
                    value = translate(value)
                rendered.append(f'{key}="{escape(value, quote=True)}"')
        self.parts.append('<' + tag + (' ' + ' '.join(rendered) if rendered else '') + '>')

    def handle_endtag(self, tag):
        if self.protected and self.protected[-1] == tag:
            self.protected.pop()
        self.parts.append('</' + tag + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.parts[-1] = self.parts[-1][:-1] + '/>'

    def handle_data(self, value):
        if self.protected and self.protected[-1] in {'script', 'style'}:
            self.parts.append(value)
        else:
            self.parts.append(escape(value if self.protected else translate(value), quote=True))

    def handle_entityref(self, name):
        self.parts.append('&' + name + ';')

    def handle_charref(self, name):
        self.parts.append('&#' + name + ';')

    def handle_decl(self, value):
        self.parts.append('<!' + value + '>')

    def handle_comment(self, value):
        self.parts.append('<!--' + value + '-->')


def translate_interface(html):
    parser = InterfaceTranslator()
    parser.feed(html)
    return ''.join(parser.parts)
