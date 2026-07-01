/* global ace */
ace.define(
  "ace/mode/idscript_highlight_rules",
  ["require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"],
  function (require, exports) {
    "use strict";

    const oop = require("ace/lib/oop");
    const TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

    const IDScriptHighlightRules = function () {
      const identifier = "[A-Za-z_][A-Za-z0-9_]*";
      const typeNames = "Teks|Angka|Float|Boolean|Kosong|Apapun|daftar|kamus|hasil";
      const typeRef = `${typeNames}|${identifier}`;
      const stringPattern = '"(?:\\\\.|[^"\\\\])*"';

      this.$rules = {
        start: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "string.quoted.double",
            regex: '"(?=.)',
            next: "qqstring",
          },
          {
            token: "constant.numeric",
            regex: "[-+]?(?:\\d+\\.\\d+|\\d+)(?:[eE][-+]?\\d+)?\\b",
          },

          // Import keywords are contextual: `dari` and `impor` are highlighted
          // only when they form a real import statement. A second rule keeps
          // multi-line imports highlighted when `{` starts on the next line.
          {
            token: [
              "keyword.control.import",
              "text",
              "string.quoted.double.import-path",
              "text",
              "keyword.control.import",
              "text",
              "paren.lparen",
            ],
            regex: `\\b(dari)(\\s+)(${stringPattern})(\\s+)(impor)(\\s*)(\\{)`,
            next: "importBlock",
          },
          {
            token: [
              "keyword.control.import",
              "text",
              "string.quoted.double.import-path",
              "text",
              "keyword.control.import",
            ],
            regex: `\\b(dari)(\\s+)(${stringPattern})(\\s+)(impor)\\b`,
            next: "beforeImportBlock",
          },

          // Declarations.
          {
            token: ["keyword.modifier", "text"],
            regex: "\\b(publik|privat)(\\s+)(?=fungsi|struktur|sifat|enum|tipe|antarmuka|implementasi|KONSTANTA|konst|metode|statik|final|var)",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.function"],
            regex: `\\b(fungsi|metode)(\\s+)(${identifier})\\b`,
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type", "text", "paren.lparen"],
            regex: `\\b(struktur)(\\s+)(${identifier})(\\s*)(\\{)`,
            next: "structBlock",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(struktur)(\\s+)(${identifier})\\b`,
            next: "beforeStructBlock",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type", "text", "paren.lparen"],
            regex: `\\b(enum)(\\s+)(${identifier})(\\s*)(\\{)`,
            next: "enumBlock",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(enum)(\\s+)(${identifier})\\b`,
            next: "beforeEnumBlock",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(sifat|antarmuka)(\\s+)(${identifier})\\b`,
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(tipe)(\\s+)(${identifier})\\b`,
          },
          {
            token: [
              "keyword.declaration",
              "text",
              "entity.name.type",
              "text",
              "keyword.declaration",
              "text",
              "entity.name.type",
            ],
            regex: `\\b(implementasi)(\\s+)(${identifier})(\\s+)(untuk)(\\s+)(${identifier})\\b`,
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(implementasi)(\\s+)(${identifier})\\b`,
          },
          {
            token: ["keyword.declaration", "text", "keyword.declaration", "text", "entity.name.type"],
            regex: `\\b(turunan)(\\s+)(dari)(\\s+)(${identifier})\\b`,
          },
          {
            token: "keyword.declaration",
            regex: `\\b(final|var|konst|KONSTANTA|konstan)(?=\\s+\\*?\\s*${identifier})`,
          },
          {
            token: "keyword.modifier",
            regex: "\\b(statik)(?=\\s+metode)",
          },

          // Control-flow keywords are contextual too.
          {
            token: ["keyword.control", "text", "keyword.control"],
            regex: "\\b(namun)(\\s+)(jika)(?=\\s*\\()",
          },
          {
            token: ["keyword.control", "text", "keyword.control"],
            regex: "\\b(jika)(\\s+)(tidak)(?=\\s*\\{)",
          },
          {
            token: "keyword.control",
            regex: "\\b(jika|untuk|selama|tangkap|pilah)(?=\\s*\\()",
          },
          {
            token: ["keyword.control", "text", "keyword.control"],
            regex: "\\b(dari)(\\s+)(dalam)\\b",
          },
          {
            token: "keyword.control",
            regex: "\\b(coba|diakhiri)(?=\\s*\\{)",
          },
          {
            token: ["keyword.control", "text", "constant.language"],
            regex: "\\b(kasus)(\\s+)(bawaan)\\b",
          },
          {
            token: "keyword.control",
            regex: "\\bkasus(?=\\s+)",
          },
          {
            token: "keyword",
            regex: "\\b(kembalikan|kesalahan|berhentikan|lanjutkan)\\b(?=\\s*(?:[({;]|$|[A-Za-z_0-9\"'\\-]))",
          },

          // Builtin types are soft keywords. They use their own token and are
          // highlighted in type positions, not as generic language keywords.
          {
            token: ["punctuation.operator", "text", "support.type"],
            regex: `(:)(\\s*)(${typeNames})\\b`,
          },
          {
            token: ["paren.lparen", "text", "support.type"],
            regex: `([\\[,])(\\s*)(${typeNames})\\b`,
          },
          {
            token: "constant.language",
            regex: "\\b(benar|salah|kosong)\\b",
          },

          // Word operators are highlighted only in operator-shaped contexts.
          {
            token: "keyword.operator",
            regex: "\\bbukan(?=\\s+)",
          },
          {
            token: ["text", "keyword.operator", "text"],
            regex: "(\\s+)(atau|dan|didalam|adalah|bukanlah)(\\s+)",
          },
          {
            token: ["text", "keyword.operator", "text", "keyword.operator", "text"],
            regex: "(\\s+)(tidak)(\\s+)(didalam|dalam)(\\s+)",
          },
          {
            token: ["text", "keyword.operator", "text"],
            regex: `(\\s+)(sebagai)(\\s+)(?=${identifier})`,
          },
          {
            token: "keyword.operator",
            regex: `\\bsalin(?=\\s+${identifier})`,
          },
          {
            token: "support.function.introspection",
            regex: `\\b(identifikasi|info)(?=\\s+${identifier})`,
          },

          {
            token: "keyword.operator.pointer",
            regex: "[&*](?=[A-Za-z_])",
          },
          {
            token: "keyword.operator",
            regex: "==|!=|>=|<=|\\*\\*|[=+\\-*/<>]",
          },
          {
            token: "punctuation.operator",
            regex: "[?:,.;]",
          },
          {
            token: "paren.lparen",
            regex: "[({\\[]",
          },
          {
            token: "paren.rparen",
            regex: "[)}\\]]",
          },
          {
            token: "identifier",
            regex: `${identifier}\\b`,
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        beforeImportBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.lparen",
            regex: "\\{",
            next: "importBlock",
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        beforeStructBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.lparen",
            regex: "\\{",
            next: "structBlock",
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        beforeEnumBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.lparen",
            regex: "\\{",
            next: "enumBlock",
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        structBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.rparen",
            regex: "\\}",
            next: "start",
          },
          {
            token: "keyword.modifier.field",
            regex: `\\b(publik|privat|statik)\\b(?=\\s*${identifier}\\s*:)`,
          },
          {
            token: ["entity.name.variable.field", "text", "punctuation.operator", "text", "support.type"],
            regex: `\\b(${identifier})(\\s*)(:)(\\s*)(${typeRef})\\b`,
          },
          {
            token: "punctuation.operator",
            regex: "[,;]",
          },
          {
            token: "paren.lparen",
            regex: "[({\\[]",
          },
          {
            token: "paren.rparen",
            regex: "[)\\]]",
          },
          {
            token: "identifier",
            regex: `${identifier}\\b`,
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        enumBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.rparen",
            regex: "\\}",
            next: "start",
          },
          {
            token: "keyword.modifier.field",
            regex: `\\b(publik|privat|statik)\\b(?=\\s*${identifier})`,
          },
          {
            token: ["entity.name.type.variant", "text", "paren.lparen"],
            regex: `\\b(${identifier})(\\s*)(\\{)`,
            next: "enumStructBlock",
          },
          {
            token: ["entity.name.type.variant", "text", "paren.lparen"],
            regex: `\\b(${identifier})(\\s*)(\\()`,
          },
          {
            token: ["entity.name.type.variant", "text", "keyword.operator"],
            regex: `\\b(${identifier})(\\s*)(=)`,
          },
          {
            token: "entity.name.type.variant",
            regex: `${identifier}\\b`,
          },
          {
            token: "punctuation.operator",
            regex: "[,;]",
          },
          {
            token: "paren.lparen",
            regex: "[({\\[]",
          },
          {
            token: "paren.rparen",
            regex: "[)\\]]",
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        enumStructBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "paren.rparen",
            regex: "\\}",
            next: "enumBlock",
          },
          {
            token: "keyword.modifier.field",
            regex: `\\b(publik|privat|statik)\\b(?=\\s*${identifier}\\s*:)`,
          },
          {
            token: ["entity.name.variable.field", "text", "punctuation.operator", "text", "support.type"],
            regex: `\\b(${identifier})(\\s*)(:)(\\s*)(${typeRef})\\b`,
          },
          {
            token: "punctuation.operator",
            regex: "[,;]",
          },
          {
            token: "paren.lparen",
            regex: "[({\\[]",
          },
          {
            token: "paren.rparen",
            regex: "[)\\]]",
          },
          {
            token: "identifier",
            regex: `${identifier}\\b`,
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        importBlock: [
          {
            token: "comment.line.double-slash",
            regex: "//.*$",
          },
          {
            token: "comment.start",
            regex: "/\\*",
            next: "comment",
          },
          {
            token: "keyword.modifier.import",
            regex: "\\b(publik|privat|var|konstan|statik)\\b",
          },
          {
            token: "keyword.control.import",
            regex: "\\bsebagai\\b",
          },
          {
            token: "constant.language.import-all",
            regex: "\\*Apapun|\\*",
          },
          {
            token: "variable.parameter.import",
            regex: `${identifier}\\b`,
          },
          {
            token: "punctuation.operator",
            regex: "[,;]",
          },
          {
            token: "paren.rparen",
            regex: "\\}",
            next: "start",
          },
          {
            token: "text",
            regex: "\\s+",
          },
        ],

        comment: [
          {
            token: "comment.end",
            regex: "\\*/",
            next: "start",
          },
          {
            defaultToken: "comment.block",
          },
        ],

        qqstring: [
          {
            token: "constant.language.escape",
            regex: "\\\\(?:[\\\\\"'nrtbf]|u[0-9a-fA-F]{4})",
          },
          {
            token: "string.quoted.double",
            regex: '"',
            next: "start",
          },
          {
            defaultToken: "string.quoted.double",
          },
        ],
      };

      this.normalizeRules();
    };

    oop.inherits(IDScriptHighlightRules, TextHighlightRules);
    exports.IDScriptHighlightRules = IDScriptHighlightRules;
  }
);

ace.define(
  "ace/mode/idscript",
  [
    "require",
    "exports",
    "module",
    "ace/lib/oop",
    "ace/mode/text",
    "ace/mode/idscript_highlight_rules",
    "ace/range",
  ],
  function (require, exports) {
    "use strict";

    const oop = require("ace/lib/oop");
    const TextMode = require("ace/mode/text").Mode;
    const IDScriptHighlightRules = require("ace/mode/idscript_highlight_rules").IDScriptHighlightRules;
    const Range = require("ace/range").Range;

    const Mode = function () {
      this.HighlightRules = IDScriptHighlightRules;
      this.$behaviour = this.$defaultBehaviour;
    };

    oop.inherits(Mode, TextMode);

    (function () {
      this.lineCommentStart = "//";
      this.blockComment = { start: "/*", end: "*/" };
      this.$id = "ace/mode/idscript";

      this.getNextLineIndent = function (state, line, tab) {
        const indent = this.$getIndent(line);
        const trimmed = line.trim();
        if (state === "start" && /[{[(]$/.test(trimmed)) return indent + tab;
        if (["importBlock", "structBlock", "enumBlock", "enumStructBlock"].includes(state)) return indent + tab;
        return indent;
      };

      this.checkOutdent = function (_state, line, input) {
        if (!/^\s+$/.test(line)) return false;
        return /^\s*[}\])]/.test(input);
      };

      this.autoOutdent = function (_state, doc, row) {
        const line = doc.getLine(row);
        const match = line.match(/^(\s*[}\])])/);
        if (!match) return;

        const column = match[1].length;
        const openBracePos = doc.findMatchingBracket({ row, column });
        if (!openBracePos || openBracePos.row === row) return;

        const indent = this.$getIndent(doc.getLine(openBracePos.row));
        doc.replace(new Range(row, 0, row, column - 1), indent);
      };
    }.call(Mode.prototype));

    exports.Mode = Mode;
  }
);
