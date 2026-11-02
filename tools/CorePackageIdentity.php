<?php

declare(strict_types=1);

namespace PDF\Tools\Documentation;

/** Keep historical consumer identities separate from the canonical documented core. */
final readonly class CorePackageIdentity
{
    public const CANONICAL = 'pdftoolkit/pdf';
    public const LEGACY = 'roukmoute/pdf';

    public string $name;

    /**
     * @param list<array<string, mixed>> $locked
     * @param list<array<string, mixed>> $installed
     */
    public function __construct(array $locked, array $installed)
    {
        $names = [];
        foreach ([$locked, $installed] as $inventory) {
            $matches = array_values(array_filter($inventory, static fn (array $record): bool => in_array($record['name'] ?? null, [self::CANONICAL, self::LEGACY], true)));
            if (count($matches) !== 1) {
                throw new \RuntimeException('Exactly one core package identity is required in lock and installation.');
            }
            $names[] = $matches[0]['name'];
        }
        if ($names[0] !== $names[1]) {
            throw new \RuntimeException('Installed core package name differs from its consumer lock.');
        }
        $this->name = $names[0];
    }
}
