import { python } from 'pythonia';

const _src      = await python('IDScript');

const Compile   = await    _src.Compile;
const IDVMToken = await  _src.IDVMToken;
const Grammar   = await    _src.Grammar;

export { Compile, IDSVMToken, Grammar };