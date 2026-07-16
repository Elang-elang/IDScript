# Generik
## Struktur
konsepnya adalah sebagai berikut

```
<publik|privat>? struktur <NAME> <type_params>? {
 <struct_fields>*
} <turunan dari <NAME> <type_params>? <;>?>
```
### penjelasan:
- `< ... >` sebuah lambang rule(s) yang ku sengaja lambangkan atau pemanggilan rule(s)
- `(\w+)` itu adalah keyword
- regex: `[regexBlock]< [regexBlock] >[regexBlock]` -> untuk melambang kan regex, regex itu berada pada kurung siku itu `[regexBlock]`. contoh `(<publik|privat>)?`

### makna:
saat struktur dinyatakan, maka ada geneeik parameter khusus untuk struktur `<NAME>` dan cara memanggilnya jadi sebagai berikut `NAME<...>`. lalu saat dia merupkan struktur turunan dari `<NAME>` yang lain, maka akan ditransfer generiknya. jadi seperti pada rust di block implementnya `impl` yang memuat generik untuk `impl` dan akan ditransfer ke structure -nya. `impl<A, B> Name<A, B>`.
untuk contoh syntax ids nya nanti adalah sebagai berikut:
```idscript
publik Map<K, V> {
    keys: daftar<K>,
    values: daftar<V>,
} turunan dari Kamus<K, V>;
```

## Enum
Samakan saja seperti Rust namun versi IDScript

## Implementasi
Samakan saja seperti Rust namun versi IDScript

## Interface
Samakan saja seperti Go/TypeScript namun versi IDScript
```
```
