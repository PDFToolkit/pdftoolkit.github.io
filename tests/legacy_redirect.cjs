"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const site = process.argv[2];
if (!site) throw new Error("Usage: node tests/legacy_redirect.cjs <legacy-site-directory>");
const manifest = JSON.parse(fs.readFileSync(path.join(site, "legacy-manifest.json"), "utf8"));
const code = fs.readFileSync(path.join(site, manifest.redirectScript.path), "utf8");
const origin = new URL(manifest.siteUrl).origin;
const base = manifest.legacyBase;

function redirect(pathname, search = "", hash = "", requestOrigin = origin, overrides = {}) {
  const replacements = [];
  const fallbackLinks = [];
  const attributes = {
    "data-site-url": manifest.siteUrl,
    "data-legacy-base": base,
    ...overrides,
  };
  const context = {
    URL,
    document: {
      currentScript: { getAttribute: name => attributes[name] },
      getElementById: id => {
        assert.equal(id, "destination");
        return { setAttribute: (name, value) => {
          assert.equal(name, "href");
          fallbackLinks.push(value);
        } };
      },
    },
    location: {
      origin: requestOrigin, pathname, search, hash,
      replace: value => replacements.push(value),
    },
  };
  vm.runInNewContext(code, context, { timeout: 1000, filename: "legacy-redirect.js" });
  assert.deepEqual(fallbackLinks, replacements, "The accessible link must preserve the same URL as the redirect");
  return replacements;
}

const positive = [
  [base, "", "", "/"],
  [base + "/", "", "", "/"],
  [base + "/reference/example.html", "?q=A%2BB&x=1&x=2", "#signature%20%C3%A9", "/reference/example.html"],
  [base + "/reference/%C3%A9%20value.html", "?next=%2Fpdf%2F&empty=", "#a%2Fb%23c", "/reference/%C3%A9%20value.html"],
  [base + "/unknown/path.html", "?unknown=true", "#preserved", "/unknown/path.html"],
  [base + "//another-host.example/path", "?x=1", "#frag", "//another-host.example/path"],
];
for (const [pathname, search, hash, suffix] of positive) {
  const expected = origin + suffix + search + hash;
  const actual = redirect(pathname, search, hash);
  assert.deepEqual(actual, [expected]);
  assert.equal(new URL(actual[0]).origin, origin, "Even double slash paths must remain on the documentation origin");
}

for (const pathname of [base + "-prefix/page.html", base + "2/", "/", "/reference/index.html", "//foreign.example" + base + "/"]) {
  assert.deepEqual(redirect(pathname, "?q=1", "#x"), [], "Only the complete legacy path prefix may redirect");
}
assert.deepEqual(redirect(base + "/", "", "", "https://another-host.example"), []);
assert.deepEqual(redirect(base + "/", "", "", origin, { "data-site-url": "javascript:alert(1)" }), []);
assert.deepEqual(redirect(base + "/", "", "", origin, { "data-site-url": "https://another-host.example/" }), []);
assert.deepEqual(redirect(base + "/", "", "", origin, { "data-site-url": manifest.siteUrl + "?unsafe=1" }), []);
assert.deepEqual(redirect(base + "/", "", "", origin, { "data-legacy-base": base + "/" }), []);

console.log("Checked redirect paths, query strings, encoded fragments, unknown routes and origin guards in an isolated JavaScript VM");
