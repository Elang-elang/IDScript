/* global ace */
ace.define(
  "ace/mode/idscript_highlight_rules",
  ["require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"],
  function (require, exports) {
    "use strict";

    const oop = require("ace/lib/oop");
    const TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

    const IDScriptHighlightRules = function () {
      const declarationKeywords = "fungsi|metode|struktur|implementasi|sifat|enum|tipe|antarmuka|turunan";
      const controlKeywords = "jika|namun|tidak|untuk|dari|dalam|selama|coba|tangkap|diakhiri|pilah|kasus|bawaan";
      const flowKeywords = "kembalikan|kesalahan|berhentikan|lanjutkan";
      const modifiers = "publik|privat|statik|final|var|konst|KONSTANTA|konstan";
      const operators = "bukan|atau|dan|didalam|adalah|bukanlah|sebagai|salin|impor";
      const constants = "benar|salah|kosong";
      const builtinTypes = "Teks|Angka|Float|Boolean|Kosong|Apapun|OBJEK|daftar|kamus|hasil";
      const builtinIntrospection = "identifikasi|info";

      const keywordMapper = this.createKeywordMapper(
        {
          "keyword.declaration": declarationKeywords,
          "keyword.control": controlKeywords,
          "keyword": flowKeywords,
          "storage.modifier": modifiers,
          "keyword.operator": operators,
          "constant.language": constants,
          "support.type": builtinTypes,
          "support.function": builtinIntrospection,
        },
        "identifier",
        true
      );

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
          {
            token: ["keyword.declaration", "text", "entity.name.function"],
            regex: "\\b(fungsi|metode)(\\s+)([A-Za-z_][A-Za-z0-9_]*)\\b",
          },
          {
            token: ["keyword.declaration", "text", "entity.name.type"],
            regex: "\\b(struktur|sifat|enum|tipe|antarmuka|implementasi)(\\s+)([A-Za-z_][A-Za-z0-9_]*)\\b",
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
            token: keywordMapper,
            regex: "[A-Za-z_][A-Za-z0-9_]*\\b",
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
