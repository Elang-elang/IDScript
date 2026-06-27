/* global acode, ace */
(function () {
  "use strict";

  const PLUGIN_ID = "idscript.syntax";
  const SCRIPT_BASE = (function () {
    if (typeof document === "undefined" || !document.currentScript) return "";
    const src = document.currentScript.src || "";
    return src.slice(0, src.lastIndexOf("/") + 1);
  })();
  let scriptsPromise = null;

  function getLanguages(baseUrl) {
    const icon = baseUrl ? `${baseUrl}small.jpg` : "small.jpg";
    return [
      {
        name: "idscript",
        caption: "IDScript",
        mode: "ace/mode/idscript",
        extensions: "ids",
        icon,
        fileIcon: icon,
        supportsFile(filename) {
          return /\.ids$/i.test(filename || "");
        },
      },
      {
        name: "idscript_module_json",
        caption: "IDScript Module JSON",
        mode: "ace/mode/json",
        extensions: "idsm|idsc",
        icon,
        fileIcon: icon,
        supportsFile(filename) {
          return /\.(idsm|idsc)$/i.test(filename || "");
        },
      },
    ];
  }

  function getAce() {
    if (typeof ace !== "undefined") return ace;
    if (typeof window !== "undefined" && window.ace) return window.ace;
    return null;
  }

  function registerModes(baseUrl) {
    const aceInstance = getAce();
    if (!aceInstance) return;

    const aceModes = typeof acode !== "undefined" && acode.require && acode.require("aceModes");
    if (aceModes && typeof aceModes.addMode === "function") {
      aceModes.addMode("idscript", ["ids"], "IDScript");
    }

    const modelist = aceInstance.require && aceInstance.require("ace/ext/modelist");
    if (!modelist || !Array.isArray(modelist.modes)) return;

    for (const language of getLanguages(baseUrl)) {
      const exists = modelist.modes.some((mode) => mode.name === language.name);
      if (!exists) modelist.modes.push(language);

      if (modelist.modesByName) modelist.modesByName[language.name] = language;
    }
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (!src) return resolve();
      const existing = document.querySelector(`script[data-idscript-plugin="${src}"]`);
      if (existing) return resolve();

      const script = document.createElement("script");
      script.src = src;
      script.dataset.idscriptPlugin = src;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Gagal memuat ${src}`));
      document.head.appendChild(script);
    });
  }

  function normalizeBaseUrl(baseUrl) {
    if (typeof baseUrl !== "string" || !baseUrl) return SCRIPT_BASE;
    return baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  }

  async function loadAceMode(baseUrl) {
    if (scriptsPromise) return scriptsPromise;

    const base = normalizeBaseUrl(baseUrl);
    if (!base) {
      registerModes(base);
      return;
    }

    scriptsPromise = Promise.all([
      loadScript(`${base}mode-idscript.js`),
      loadScript(`${base}snippets/idscript.js`),
    ]).then(() => registerModes(base));
    return scriptsPromise;
  }

  function unregisterMode() {
    const aceInstance = getAce();
    if (!aceInstance) return;

    const aceModes = typeof acode !== "undefined" && acode.require && acode.require("aceModes");
    if (aceModes && typeof aceModes.removeMode === "function") {
      aceModes.removeMode("idscript");
    }

    const modelist = aceInstance.require && aceInstance.require("ace/ext/modelist");
    if (!modelist || !Array.isArray(modelist.modes)) return;

    for (const language of getLanguages("")) {
      const index = modelist.modes.findIndex((mode) => mode.name === language.name);
      if (index >= 0) modelist.modes.splice(index, 1);
      if (modelist.modesByName) delete modelist.modesByName[language.name];
    }
  }

  async function init(baseUrl) {
    await loadAceMode(baseUrl);
  }

  async function destroy() {
    unregisterMode();
  }

  if (typeof acode !== "undefined") {
    acode.setPluginInit(PLUGIN_ID, async (baseUrl) => init(baseUrl));
    acode.setPluginUnmount(PLUGIN_ID, destroy);
  } else if (typeof window !== "undefined") {
    window.IDScriptAcodePlugin = { init, destroy, registerModes, unregisterMode };
  }
})();
