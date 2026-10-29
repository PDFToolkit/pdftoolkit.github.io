"""Check the identical FR/EN heading contract before expensive package oracles."""
from pathlib import Path

import markdown
from localization import LANGUAGES, localized_source


def headings(text: str) -> list[dict]:
    renderer = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'])
    renderer.convert(text)

    def flatten(tokens):
        return [value for token in tokens for value in [token, *flatten(token.get('children', []))]]

    return flatten(renderer.toc_tokens)


def translated_anchors(pages: list[tuple], roots: dict[str, Path]) -> dict[str, dict]:
    anchors = {}
    for owner, source, route, _, _ in pages:
        tokens = {language: headings((roots[owner] / localized_source(owner, source, language)).read_text(encoding='utf-8')) for language in LANGUAGES}
        if [token['level'] for token in tokens['en']] != [token['level'] for token in tokens['fr']]:
            raise ValueError('Translated heading structure differs: ' + owner + ':' + source)
        anchors[route] = {
            'en': {en['id']: fr['id'] for en, fr in zip(tokens['en'], tokens['fr']) if en['level'] > 1},
            'fr': {fr['id']: en['id'] for en, fr in zip(tokens['en'], tokens['fr']) if fr['level'] > 1},
        }
    return anchors
