"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Use the source by default, or pass a built site's script to validate its artifact.
const scriptPath = process.argv[2] || path.join(__dirname, "../docs/site/assets/site.js");
const script = fs.readFileSync(scriptPath, "utf8");
let checks = 0;

class NodeStub {
  constructor(tagName = "div") {
    this.tagName = tagName;
    this.attributes = new Map();
    this.dataset = {};
    this.children = [];
    this.afterNodes = [];
    this.events = new Map();
    this.textContent = "";
    this.hidden = false;
    this.value = "";
    const classes = new Set();
    this.classList = {
      add: (...names) => names.forEach(name => classes.add(name)),
      remove: (...names) => names.forEach(name => classes.delete(name)),
      contains: name => classes.has(name),
      toggle: (name, force) => {
        const present = force === undefined ? !classes.has(name) : force;
        if (present) classes.add(name);
        else classes.delete(name);
        return present;
      },
    };
  }

  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.get(name) ?? null; }
  set href(value) { this.setAttribute("href", value); }
  get href() { return this.getAttribute("href"); }
  append(...nodes) { this.children.push(...nodes); }
  after(...nodes) { this.afterNodes.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes.flatMap(node => node.tagName === "fragment" ? node.children : [node]); }
  querySelector(selector) { return selector === "code" ? this.children.find(node => node.tagName === "code") || null : null; }
  addEventListener(name, listener) {
    this.events.set(name, [...(this.events.get(name) || []), listener]);
  }
  async emit(name, event = {}) {
    await Promise.all((this.events.get(name) || []).map(listener => listener(event)));
  }
}

function page(options = {}) {
  let address = new URL(options.url || "https://pdftoolkit.github.io/guides/components.html");
  const documentBase = address.href;
  const elements = new Map();
  const events = new Map();
  const timers = new Map();
  const replacements = [];
  const clipboard = [];
  let nextTimer = 0;
  const main = new NodeStub("main");
  main.dataset.root = options.root || "/";
  elements.set("main", main);
  const links = (options.links || []).map(({ href, anchors }) => {
    const link = new NodeStub("a");
    link.href = href;
    link.dataset.anchorMap = typeof anchors === "string" ? anchors : JSON.stringify(anchors || {});
    return link;
  });
  const blocks = [];
  if (Object.hasOwn(options, "code")) {
    const block = new NodeStub("pre");
    const code = new NodeStub("code");
    code.textContent = options.code;
    block.append(code);
    blocks.push(block);
  }
  if (options.redirect !== undefined) {
    main.dataset.redirectTo = options.redirect;
    elements.set("destination", new NodeStub("a"));
  }
  if (options.search) {
    for (const id of ["component-search", "search-results", "search-status", "component-list"]) {
      elements.set(id, new NodeStub(id === "component-search" ? "input" : "div"));
    }
    elements.get("component-search").dataset.searchIndex = options.lang === "fr"
      ? "/assets/search-index.fr.json" : "/assets/search-index.json";
  }
  const location = {
    get href() { return address.href; },
    get origin() { return address.origin; },
    get pathname() { return address.pathname; },
    get search() { return address.search; },
    get hash() { return address.hash; },
    replace: target => replacements.push(target),
  };
  const document = {
    documentElement: { lang: options.lang || "en" },
    baseURI: documentBase,
    getElementById: id => elements.get(id) || null,
    querySelector: selector => selector === "main" ? main
      : selector === "main[data-redirect-to]" && options.redirect !== undefined ? main : null,
    querySelectorAll: selector => selector === "a[data-language-link]" ? links : selector === "pre" ? blocks : [],
    createElement: tag => new NodeStub(tag),
    createDocumentFragment: () => new NodeStub("fragment"),
    addEventListener() {},
  };
  const window = {
    location,
    isSecureContext: options.secure !== false,
    addEventListener: (name, callback) => events.set(name, [...(events.get(name) || []), callback]),
    history: { replaceState: (_state, _title, url) => { address = new URL(url); } },
  };
  const navigator = options.noClipboard ? {} : {
    clipboard: {
      writeText: async value => {
        if (options.clipboardFailure) throw new Error("Clipboard denied");
        clipboard.push(value);
      },
    },
  };
  const requests = [];
  const context = {
    URL, document, window, navigator, Node: NodeStub, Element: NodeStub,
    setTimeout: (callback, delay) => { const id = ++nextTimer; timers.set(id, { callback, delay }); return id; },
    clearTimeout: id => timers.delete(id),
    fetch: async url => {
      requests.push(String(url));
      if (options.searchFailure) throw new Error("Unavailable");
      return { ok: true, text: async () => JSON.stringify(options.records || []) };
    },
  };
  vm.runInNewContext(script, context, { filename: scriptPath, timeout: 1000 });
  return {
    links, blocks, elements, replacements, clipboard, requests, location,
    async emit(name) { await Promise.all((events.get(name) || []).map(listener => listener({}))); },
    async settle() { for (let i = 0; i < 12; i++) await Promise.resolve(); },
    setAddress(url) { address = new URL(url, address); },
    async runTimers(delay) {
      for (const [id, timer] of [...timers]) {
        if (timer.delay !== delay) continue;
        timers.delete(id);
        await timer.callback();
      }
    },
  };
}

async function check(name, test) {
  await test();
  checks++;
  console.log("ok - " + name);
}

async function run() {
  await check("Language switching preserves a demo selection changed through history.replaceState", async () => {
    for (const event of ["click", "pointerdown", "focus", "contextmenu"]) {
      const demo = page({
        url: "https://pdftoolkit.github.io/modules/to-html/demo/index.html?sample=structure",
        links: [{ href: "/fr/modules/to-html/demo/index.html" }],
      });
      demo.setAddress("https://pdftoolkit.github.io/modules/to-html/demo/index.html?sample=mathml#preview");
      await demo.links[0].emit(event);
      assert.equal(demo.links[0].href, "https://pdftoolkit.github.io/fr/modules/to-html/demo/index.html?sample=mathml#preview");
    }
  });
  await check("Switch languages on the corresponding page without losing filters or an encoded anchor", async () => {
    const en = page({
      url: "https://pdftoolkit.github.io/guides/components.html?q=A%2BB&kind=class&x=1&x=2#string-bytes-and-unicode-text",
      links: [{ href: "/fr/guides/composants.html", anchors: { "string-bytes-and-unicode-text": "octets-dune-chaîne-et-texte-unicode" } }],
    });
    const french = new URL(en.links[0].href);
    assert.equal(french.origin, en.location.origin);
    assert.equal(french.pathname, "/fr/guides/composants.html");
    assert.equal(french.search, "?q=A%2BB&kind=class&x=1&x=2");
    assert.equal(decodeURIComponent(french.hash.slice(1)), "octets-dune-chaîne-et-texte-unicode");
    const fr = page({ lang: "fr", url: french.href, links: [{
      href: "/guides/components.html", anchors: { "octets-dune-chaîne-et-texte-unicode": "string-bytes-and-unicode-text" },
    }] });
    assert.equal(fr.links[0].href, en.location.href, "The return switch must recover the English section and query");
  });

  await check("The switch follows later hash changes and preserves anchors shared by both languages", async () => {
    const app = page({ url: "https://pdftoolkit.github.io/reference/example.html?q=Font#method-toPdf", links: [{ href: "/fr/reference/example.html" }] });
    assert.equal(new URL(app.links[0].href).hash, "#method-toPdf");
    app.setAddress("#property-%C3%A9%20a%2Fb");
    await app.emit("hashchange");
    const destination = new URL(app.links[0].href);
    assert.equal(destination.search, "?q=Font");
    assert.equal(decodeURIComponent(destination.hash.slice(1)), "property-é a/b");
  });

  await check("An unknown fragment does not disappear, and inherited object names do not become mappings", async () => {
    for (const fragment of ["unknown-heading", "constructor", "toString", "__proto__"]) {
      const app = page({ url: "https://pdftoolkit.github.io/guides/components.html#" + fragment,
        links: [{ href: "/fr/guides/composants.html", anchors: { unrelated: "autre" } }] });
      assert.equal(new URL(app.links[0].href).hash, "#" + fragment);
    }
  });

  await check("Invalid mapping metadata keeps a usable static language link", async () => {
    const app = page({ url: "https://pdftoolkit.github.io/guides/components.html#values",
      links: [{ href: "/fr/guides/composants.html", anchors: "{invalid json" }] });
    assert.equal(app.links[0].href, "/fr/guides/composants.html");
  });

  await check("A language switch does not rewrite a foreign or out-of-prefix destination", async () => {
    for (const href of ["https://another-host.example/fr/", "//another-host.example/fr/", "/documentation2/fr/", "javascript:alert(1)", "/documentation/../elsewhere/"]) {
      const app = page({ url: "https://pdftoolkit.github.io/documentation/index.html?q=1#x", root: "/documentation/", links: [{ href }] });
      assert.equal(app.links[0].href, href);
      assert.deepEqual(app.replacements, []);
    }
  });

  await check("Old French route aliases return to the French page with query and fragment intact", async () => {
    const app = page({ url: "https://pdftoolkit.github.io/guides/demarrer.html?q=Font&kind=class#installation",
      redirect: "/fr/guides/demarrer.html" });
    const expected = "https://pdftoolkit.github.io/fr/guides/demarrer.html?q=Font&kind=class#installation";
    assert.deepEqual(app.replacements, [expected]);
    assert.equal(app.elements.get("destination").href, expected, "The accessible fallback link must match the redirect");
  });

  await check("Aliases never turn query data into an external redirect", async () => {
    const app = page({ url: "https://pdftoolkit.github.io/guides/demarrer.html?next=https%3A%2F%2Fanother-host.example#https://another-host.example",
      redirect: "/fr/guides/demarrer.html" });
    assert.equal(app.replacements.length, 1);
    assert.equal(new URL(app.replacements[0]).origin, app.location.origin);
    assert.equal(new URL(app.replacements[0]).search, app.location.search);
    assert.equal(new URL(app.replacements[0]).hash, app.location.hash);
  });

  await check("Aliases reject external origins and routes outside a hosted subdirectory", async () => {
    for (const redirect of ["https://another-host.example/fr/", "//another-host.example/fr/", "javascript:alert(1)", "/documentation2/fr/", "/documentation/../elsewhere/"]) {
      const app = page({ url: "https://pdftoolkit.github.io/documentation/guides/demarrer.html", root: "/documentation/", redirect });
      assert.deepEqual(app.replacements, []);
      assert.equal(app.elements.get("destination").href, null);
    }
  });

  await check("An incorrect declared root cannot authorize a redirect away from the current origin", async () => {
    const app = page({ url: "https://pdftoolkit.github.io/guides/demarrer.html",
      root: "https://another-host.example/", redirect: "https://another-host.example/fr/" });
    assert.deepEqual(app.replacements, []);
  });

  for (const [lang, text] of [
    ["en", { initial: "Copy", done: "Copied", label: "Copy this code block", success: "Code copied to the clipboard.", failure: "Copying is unavailable. Select the code to copy it." }],
    ["fr", { initial: "Copier", done: "Copié", label: "Copier ce bloc de code", success: "Code copié dans le presse-papiers.", failure: "La copie n’est pas disponible. Sélectionnez le code pour le copier." }],
  ]) {
    await check("Copy code and announce success in " + lang + " without changing its bytes", async () => {
      const code = "<?php\n$nom = 'é & <PDF>';\n";
      const app = page({ lang, code });
      const button = app.blocks[0].children.find(node => node.tagName === "button");
      const status = app.blocks[0].afterNodes[0];
      assert.equal(button.textContent, text.initial);
      assert.equal(button.getAttribute("aria-label"), text.label);
      assert.equal(status.getAttribute("role"), "status");
      assert.equal(status.getAttribute("aria-live"), "polite");
      await button.emit("click");
      assert.deepEqual(app.clipboard, [code]);
      assert.equal(button.textContent, text.done);
      assert.equal(status.textContent, text.success);
      await app.runTimers(2200);
      assert.equal(button.textContent, text.initial);
    });
    await check("Denied clipboard access offers a visible localized fallback in " + lang, async () => {
      const app = page({ lang, code: "<?php echo 'PDF';", clipboardFailure: true });
      const button = app.blocks[0].children.find(node => node.tagName === "button");
      const status = app.blocks[0].afterNodes[0];
      await button.emit("click");
      assert.deepEqual(app.clipboard, []);
      assert.equal(button.textContent, text.initial);
      assert.equal(status.textContent, text.failure);
      assert.equal(status.classList.contains("visually-hidden"), false);
    });
    await check("Search results use their own locale and preserve live filters in " + lang + " switching links", async () => {
      const app = page({ lang, search: true,
        url: "https://pdftoolkit.github.io/" + (lang === "fr" ? "fr/" : "") + "reference/index.html?q=Font&keep=1#component-list",
        links: [{ href: lang === "fr" ? "/reference/index.html" : "/fr/reference/index.html" }],
        records: [{ title: "PDF\\Font", shortName: "Font", kind: "class", url: (lang === "fr" ? "fr/" : "") + "reference/Font.html", optional: true, package: "pdftoolkit/pdf-fonts" },
          { title: "Foreign Font", shortName: "Font", kind: "class", url: "https://another-host.example/Font.html" }],
      });
      await app.settle();
      assert.equal(app.requests[0], "https://pdftoolkit.github.io/assets/search-index" + (lang === "fr" ? ".fr" : "") + ".json");
      const cards = app.elements.get("search-results").children;
      assert.equal(cards.length, 1);
      assert.equal(new URL(cards[0].href).pathname, (lang === "fr" ? "/fr" : "") + "/reference/Font.html");
      assert.equal(app.elements.get("search-status").textContent, lang === "fr" ? "1 composant trouvé." : "1 component found.");
      assert.equal(cards[0].children[3].textContent, (lang === "fr" ? "Optionnel" : "Optional") + " · pdftoolkit/pdf-fonts");
      app.elements.get("component-search").value = "Stream";
      await app.elements.get("component-search").emit("input");
      await app.runTimers(160);
      await app.settle();
      const switchUrl = new URL(app.links[0].href);
      assert.equal(switchUrl.searchParams.get("q"), "Stream");
      assert.equal(switchUrl.searchParams.get("keep"), "1");
      assert.equal(switchUrl.hash, "#component-list");
      assert.equal(app.elements.get("search-results").children[0].textContent, lang === "fr"
        ? "Aucun composant ne correspond à cette recherche. Essayez un nom PDF comme Catalog, Font ou Stream."
        : "No components match this search. Try a PDF name such as Catalog, Font or Stream.");
    });
  }

  await check("Unavailable clipboard support leaves code readable without a broken copy button", async () => {
    for (const options of [{ noClipboard: true }, { secure: false }]) {
      const app = page({ code: "<?php echo 'PDF';", ...options });
      assert.equal(app.blocks[0].children.length, 1);
      assert.equal(app.blocks[0].children[0].textContent, "<?php echo 'PDF';");
    }
  });
  console.log(`Checked ${checks} user-facing language, clipboard, search and redirect scenarios`);
}

run().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
