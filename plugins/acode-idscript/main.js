/* global acode, ace, editorManager */
(function () {
  "use strict";

  const PLUGIN_ID = "idscript.syntax";

  const LANGUAGES = [
    { name: "idscript", caption: "IDScript", exts: ["ids"] },
    { name: "idscript_module", caption: "IDScript Module", exts: ["idsm"] },
    { name: "idscript_compiled", caption: "IDScript Compiled", exts: ["idsc"] },
  ];

  function isCodeMirror() {
    return !!(editorManager && editorManager.isCodeMirror);
  }

  function resolveIcon(baseUrl, file) {
    const base = typeof baseUrl === "string" && baseUrl ? baseUrl : "";
    return base + file;
  }

  function getLanguageDescriptors(baseUrl) {
    const iconFile = resolveIcon(baseUrl, "small.jpg");
    return LANGUAGES.map((lang) => ({
      ...lang,
      icon: iconFile,
      fileIcon: iconFile,
      supportsFile(filename) {
        return lang.exts.some((ext) => {
          const re = new RegExp("\\.(" + ext + ")$", "i");
          return re.test(filename || "");
        });
      },
    }));
  }

  function registerAceModes(baseUrl) {
    const aceModes =
      typeof acode !== "undefined" &&
      acode.require &&
      acode.require("aceModes");
    if (aceModes && typeof aceModes.addMode === "function") {
      for (const lang of LANGUAGES) {
        aceModes.addMode(lang.name, lang.exts, lang.caption);
      }
    }

    if (typeof ace === "undefined" || !ace.require) return;

    const modelist =
      ace.require && ace.require("ace/ext/modelist");
    if (!modelist || !Array.isArray(modelist.modes)) return;

    for (const desc of getLanguageDescriptors(baseUrl)) {
      const exists = modelist.modes.some((m) => m.name === desc.name);
      if (!exists) modelist.modes.push(desc);
      if (modelist.modesByName) modelist.modesByName[desc.name] = desc;
    }
  }

  function registerCMModes() {
    const editorLanguages =
      typeof acode !== "undefined" &&
      acode.require &&
      acode.require("editorLanguages");
    if (!editorLanguages || typeof editorLanguages.register !== "function")
      return;

    for (const lang of LANGUAGES) {
      editorLanguages.register(lang.name, lang.exts, lang.caption);
    }
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (!src) return resolve();
      const existing = document.querySelector(
        'script[data-idscript-plugin="' + src + '"]'
      );
      if (existing) return resolve();
      const script = document.createElement("script");
      script.src = src;
      script.dataset.idscriptPlugin = src;
      script.onload = resolve;
      script.onerror = function () {
        console.warn("[IDScript] Gagal memuat " + src);
        resolve();
      };
      document.head.appendChild(script);
    });
  }

  function loadAceModeFiles(baseUrl) {
    var base = typeof baseUrl === "string" ? baseUrl : "";
    if (base && !base.endsWith("/")) base += "/";

    return Promise.all([
      loadScript(base + "mode-idscript.js"),
      loadScript(base + "mode-idscript-module.js"),
      loadScript(base + "theme-idscript-night.js"),
      loadScript(base + "snippets/idscript.js"),
    ]).then(function () {
      registerAceModes(base);
    });
  }

  async function init(baseUrl) {
    if (isCodeMirror()) {
      registerCMModes();
    } else {
      await loadAceModeFiles(baseUrl);
    }
  }

  function unregisterModes() {
    var i, index;

    if (isCodeMirror()) {
      var editorLanguages =
        acode.require && acode.require("editorLanguages");
      if (editorLanguages && typeof editorLanguages.unregister === "function") {
        for (i = 0; i < LANGUAGES.length; i++) {
          editorLanguages.unregister(LANGUAGES[i].name);
        }
      }
      return;
    }

    var aceModes = acode.require && acode.require("aceModes");
    if (aceModes && typeof aceModes.removeMode === "function") {
      for (i = 0; i < LANGUAGES.length; i++) {
        aceModes.removeMode(LANGUAGES[i].name);
      }
    }

    if (typeof ace === "undefined" || !ace.require) return;
    var modelist = ace.require && ace.require("ace/ext/modelist");
    if (!modelist || !Array.isArray(modelist.modes)) return;

    for (i = 0; i < LANGUAGES.length; i++) {
      index = modelist.modes.findIndex(function (m) {
        return m.name === LANGUAGES[i].name;
      });
      if (index >= 0) modelist.modes.splice(index, 1);
      if (modelist.modesByName)
        delete modelist.modesByName[LANGUAGES[i].name];
    }
  }

  async function destroy() {
    unregisterModes();
  }

  if (typeof acode !== "undefined") {
    acode.setPluginInit(PLUGIN_ID, init);
    acode.setPluginUnmount(PLUGIN_ID, destroy);
  } else if (typeof window !== "undefined") {
    window.IDScriptAcodePlugin = {
      init: function (baseUrl) {
        if (isCodeMirror()) registerCMModes();
        else return loadAceModeFiles(baseUrl);
      },
      destroy: destroy,
    };
  }
})();
