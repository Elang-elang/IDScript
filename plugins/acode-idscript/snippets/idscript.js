/* global ace */
ace.define("ace/snippets/idscript", ["require", "exports", "module"], function (_require, exports) {
  "use strict";

  exports.snippetText = [
    "snippet fungsi",
    "\tfungsi ${1:nama}(${2}): ${3:Angka} {",
    "\t\t${4}",
    "\t}",
    "snippet utama",
    "\tfungsi utama(): Angka {",
    "\t\t${1:kembalikan 0;}",
    "\t}",
    "snippet jika",
    "\tjika (${1:kondisi}) {",
    "\t\t${2}",
    "\t}",
    "snippet coba",
    "\tcoba {",
    "\t\t${1}",
    "\t} tangkap (${2:e}) {",
    "\t\t${3}",
    "\t} diakhiri {",
    "\t\t${4}",
    "\t}",
    "snippet struktur",
    "\tstruktur ${1:Nama} {",
    "\t\t${2:field}: ${3:Angka}",
    "\t}",
    "snippet implementasi",
    "\timplementasi ${1:Nama} {",
    "\t\tmetode ${2:nama}(${3}): ${4:Kosong} {",
    "\t\t\t${5}",
    "\t\t}",
    "\t}",
  ].join("\n");

  exports.scope = "idscript";
});
