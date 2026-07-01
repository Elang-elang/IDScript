/* global ace */
ace.define(
  "ace/mode/idscript_module_highlight_rules",
  ["require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"],
  function (require, exports) {
    "use strict";

    const oop = require("ace/lib/oop");
    const TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

    const IDScriptModuleHighlightRules = function () {
      this.$rules = {
        start: [
          {
            token: "keyword.declaration.magic",
            regex: "^(?:IDSM1|IDSC1)$",
          },
          {
            token: "string.quoted.double",
            regex: '"(?:\\\\.|[^"\\\\])*"',
          },
          {
            token: "constant.language",
            regex: "\\b(?:true|false|null)\\b",
          },
          {
            token: "constant.numeric",
            regex: "-?(?:0|[1-9]\\d*)(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b",
          },
          {
            token: "paren.lparen",
            regex: "[\\[{]",
          },
          {
            token: "paren.rparen",
            regex: "[\\]}]",
          },
          {
            token: "punctuation.operator",
            regex: "[:,]",
          },
          {
            token: "text",
            regex: "\\s+",
          },
          {
            token: "text.binary",
            regex: ".+",
          },
        ],
      };

      this.normalizeRules();
    };

    oop.inherits(IDScriptModuleHighlightRules, TextHighlightRules);
    exports.IDScriptModuleHighlightRules = IDScriptModuleHighlightRules;
  }
);

ace.define(
  "ace/mode/idscript_module",
  [
    "require",
    "exports",
    "module",
    "ace/lib/oop",
    "ace/mode/text",
    "ace/mode/idscript_module_highlight_rules",
    "ace/range",
  ],
  function (require, exports) {
    "use strict";

    const oop = require("ace/lib/oop");
    const TextMode = require("ace/mode/text").Mode;
    const IDScriptModuleHighlightRules = require("ace/mode/idscript_module_highlight_rules").IDScriptModuleHighlightRules;
    const Range = require("ace/range").Range;

    const Mode = function () {
      this.HighlightRules = IDScriptModuleHighlightRules;
      this.$behaviour = this.$defaultBehaviour;
    };

    oop.inherits(Mode, TextMode);

    (function () {
      this.lineCommentStart = "";
      this.$id = "ace/mode/idscript_module";

      this.getNextLineIndent = function (_state, line, tab) {
        const indent = this.$getIndent(line);
        if (/[{[]\s*$/.test(line.trim())) return indent + tab;
        return indent;
      };

      this.checkOutdent = function (_state, line, input) {
        if (!/^\s+$/.test(line)) return false;
        return /^\s*[}\]]/.test(input);
      };

      this.autoOutdent = function (_state, doc, row) {
        const line = doc.getLine(row);
        const match = line.match(/^(\s*[}\]])/);
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
