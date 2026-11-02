<?php

declare(strict_types=1);

namespace PDF\Tools\Documentation;

/** Preserve the actual owner of inherited methods implemented by locked dependencies. */
final readonly class ApiSourceLocator
{
    /** @param array<string, array<string, mixed>> $packages */
    public function __construct(private array $packages)
    {
    }

    /** @return array<string, mixed> */
    public function locate(string $file): array
    {
        $file = realpath($file) ?: throw new \RuntimeException('Cannot resolve an API source file.');
        $sources = [];
        foreach ($this->packages as $package) {
            foreach ($package['externalSources'] ?? [] as $name => $source) {
                $sources[$name] = $source;
            }
        }
        $sources += array_reverse($this->packages, true);
        foreach ($sources as $name => $source) {
            if (!str_starts_with($file, $source['root'] . DIRECTORY_SEPARATOR)) {
                continue;
            }
            $relative = str_replace('\\', '/', substr($file, strlen($source['root']) + 1));
            if (str_starts_with($relative, 'vendor/')) {
                throw new \RuntimeException('API source belongs to an unselected dependency: ' . $file);
            }
            return [
                'package' => $name,
                'repository' => $source['repository'],
                'revision' => $source['revision'],
                'version' => $source['version'],
                'optional' => $source['optional'],
                'source' => $relative,
            ];
        }
        throw new \RuntimeException('An API declaration is outside the documented source trees.');
    }
}
