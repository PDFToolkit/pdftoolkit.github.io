"""Bind the native text example to its complete independent PDF/browser evidence."""

from dataclasses import dataclass
import hashlib
import re
from typing import ClassVar


@dataclass(frozen=True)
class TextSpacingEvidence:
    PDF_CHECKS: ClassVar[int] = 125
    BROWSER_CHECKS: ClassVar[int] = 43

    receipt: dict
    report: dict
    browsers: dict

    @staticmethod
    def passed_checks(report, expected_count):
        checks = report.get('checks')
        return (isinstance(checks, list) and len(checks) == expected_count
                and type(report.get('comparisons')) is int and report['comparisons'] == len(checks)
                and all(isinstance(check, dict) and check.get('passed') is True for check in checks))

    def validate(self, source_hash, pdf_hash, font_hash):
        receipt = self.receipt
        if (receipt.get('engine') != 'native-php' or type(receipt.get('pages')) is not int
                or receipt['pages'] != 3 or receipt.get('diagnostics') != []
                or receipt.get('sourceSha256') != source_hash or receipt.get('pdfSha256') != pdf_hash
                or not isinstance(font_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', font_hash)
                or receipt.get('fonts') != [{'family': 'Noto Sans (explicit fallback)', 'sha256': font_hash}]):
            raise ValueError('Text-spacing receipt does not bind the source, font and three-page PDF')
        if (self.report.get('status') != 'pass' or self.report.get('receipt') != receipt
                or not self.passed_checks(self.report, self.PDF_CHECKS)):
            raise ValueError('Text-spacing independent validation is incomplete or failed')
        browsers = self.browsers
        if (browsers.get('status') != 'pass' or browsers.get('sourceSha256') != source_hash
                or browsers.get('fontSha256') != font_hash or not isinstance(browsers.get('browsers'), dict)
                or set(browsers['browsers']) != {'chromium', 'firefox'}):
            raise ValueError('Text-spacing browser evidence does not bind both engines to the source and font')
        for observation in browsers['browsers'].values():
            if (not isinstance(observation, dict) or observation.get('passed') is not True
                    or not isinstance(observation.get('version'), str) or not observation['version']
                    or not self.passed_checks(observation, self.BROWSER_CHECKS)):
                raise ValueError('Text-spacing browser checks are incomplete or failed')
            binding = observation.get('fontBinding')
            if (not isinstance(binding, dict) or type(binding.get('faces')) is not int
                    or binding != {'family': 'ExplicitWitness', 'status': 'loaded', 'faces': 1}):
                raise ValueError('Text-spacing browser font must be the single loaded explicit witness')
        renders = self.report.get('renders')
        if (not isinstance(renders, list) or len(renders) != 3
                or any(not isinstance(render, dict) or render.get('file') != f'native-{number}.png'
                       or not isinstance(render.get('sha256'), str)
                       or not re.fullmatch(r'[0-9a-f]{64}', render['sha256'])
                       for number, render in enumerate(renders, 1))):
            raise ValueError('Text-spacing validation must retain every native preview in page order')

    def validate_previews(self, directory, prefix):
        for number, render in enumerate(self.report['renders'], 1):
            image = directory / f'{prefix}{number}.png'
            if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != render['sha256']:
                raise ValueError('Text-spacing preview differs from the independently validated native rendering')
