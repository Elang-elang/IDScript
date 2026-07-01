/* global ace */
ace.define("ace/theme/idscript_night", ["require", "exports", "module", "ace/lib/dom"], function (require, exports) {
  "use strict";

  exports.isDark = true;
  exports.cssClass = "ace-idscript-night";
  exports.cssText = `
.ace-idscript-night {
  background-color: #11131a;
  color: #cdd6f4;
}
.ace-idscript-night .ace_gutter {
  background: #0b0d14;
  color: #6c7086;
}
.ace-idscript-night .ace_print-margin {
  width: 1px;
  background: #313244;
}
.ace-idscript-night .ace_cursor {
  color: #f5e0dc;
}
.ace-idscript-night .ace_marker-layer .ace_selection {
  background: #313244;
}
.ace-idscript-night.ace_multiselect .ace_selection.ace_start {
  box-shadow: 0 0 3px 0 #11131a;
}
.ace-idscript-night .ace_marker-layer .ace_step {
  background: #f9e2af;
}
.ace-idscript-night .ace_marker-layer .ace_bracket {
  margin: -1px 0 0 -1px;
  border: 1px solid #6c7086;
}
.ace-idscript-night .ace_marker-layer .ace_active-line {
  background: #181b25;
}
.ace-idscript-night .ace_gutter-active-line {
  background-color: #181b25;
}
.ace-idscript-night .ace_marker-layer .ace_selected-word {
  border: 1px solid #45475a;
}
.ace-idscript-night .ace_invisible {
  color: #45475a;
}
.ace-idscript-night .ace_keyword,
.ace-idscript-night .ace_storage {
  color: #cba6f7;
  font-weight: 600;
}
.ace-idscript-night .ace_keyword.ace_operator {
  color: #89dceb;
  font-weight: 500;
}
.ace-idscript-night .ace_constant {
  color: #fab387;
}
.ace-idscript-night .ace_constant.ace_language {
  color: #f38ba8;
}
.ace-idscript-night .ace_support.ace_type {
  color: #94e2d5;
  font-style: italic;
}
.ace-idscript-night .ace_support.ace_function {
  color: #89b4fa;
}
.ace-idscript-night .ace_entity.ace_name.ace_function {
  color: #89b4fa;
}
.ace-idscript-night .ace_entity.ace_name.ace_type {
  color: #f9e2af;
}
.ace-idscript-night .ace_variable.ace_parameter {
  color: #f2cdcd;
}
.ace-idscript-night .ace_string {
  color: #a6e3a1;
}
.ace-idscript-night .ace_comment {
  color: #6c7086;
  font-style: italic;
}
.ace-idscript-night .ace_numeric {
  color: #fab387;
}
.ace-idscript-night .ace_paren,
.ace-idscript-night .ace_punctuation {
  color: #bac2de;
}
`;

  const dom = require("ace/lib/dom");
  dom.importCssString(exports.cssText, exports.cssClass);
});
