<?php

declare(strict_types=1);

namespace PDF\Tools\Documentation;

/** Keep one documented namespace on its selected source tree, never an older consumer vendor. */
final readonly class SelectedSourceAutoloader
{
    private string $root;

    public function __construct(private string $prefix, string $root)
    {
        if ($prefix === '' || !str_ends_with($prefix, '\\')) {
            throw new \InvalidArgumentException('A selected namespace needs a trailing separator.');
        }
        $this->root = realpath($root) ?: throw new \RuntimeException('Missing selected namespace source tree.');
    }

    public function register(): void
    {
        foreach ([...get_declared_classes(), ...get_declared_interfaces(), ...get_declared_traits()] as $name) {
            if (strncasecmp($name, $this->prefix, strlen($this->prefix)) === 0) {
                throw new \RuntimeException('Declarations were loaded before source selection: ' . $name);
            }
        }
        spl_autoload_register($this->load(...), true, true);
    }

    public function load(string $name): void
    {
        if (!str_starts_with($name, $this->prefix)) {
            return;
        }
        $relative = substr($name, strlen($this->prefix));
        if (preg_match('/^[A-Za-z_][A-Za-z0-9_]*(?:\\\\[A-Za-z_][A-Za-z0-9_]*)*$/D', $relative) !== 1) {
            throw new \RuntimeException('Invalid selected declaration name: ' . $name);
        }
        $path = $this->root . '/' . str_replace('\\', '/', $relative) . '.php';
        $real = realpath($path);
        if ($real === false || !is_file($real) || !str_starts_with($real, $this->root . DIRECTORY_SEPARATOR)) {
            throw new \RuntimeException('Declaration missing from the selected source: ' . $name);
        }
        require $real;
        if (!class_exists($name, false) && !interface_exists($name, false) && !trait_exists($name, false) && !enum_exists($name, false)) {
            throw new \RuntimeException('Selected source did not declare the requested symbol: ' . $name);
        }
    }
}
