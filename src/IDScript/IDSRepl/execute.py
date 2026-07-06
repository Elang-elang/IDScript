from ..compile.compile import Compile as _Helper
from ..compile.exceptions import SourceSpan, IDSError, _highlight_source_line

FileName = "__idscript_input__"
_RUNTIME = _Helper.make_interpreter()

COUNTER = 1

def span_maker(**kwargs):
    return SourceSpan(
        file=f'{FileName}',
        line=kwargs.get('line', COUNTER),
        column=kwargs.get('column', 1),
        end_line=kwargs.get('end_line', 1),
        end_column=kwargs.get('end_column', 1),
        source=kwargs.get('source', None)
    )

def except_maker(error, **kwargs):
    message = ""
    help_text = None
    
    if isinstance(error, IDSError):
        message = error.message
        help_text = error.help_text
    elif hasattr(error, 'message'):
        message = error.message
    else:
        message = str(error)

    span = span_maker(**kwargs)

    return IDSError(message, span=span, context=kwargs.get('source'), help_text=help_text, cause=error)



def _eval(raw_code):
    global COUNTER
    name = f"__ids_input__{COUNTER}"
    code = f"fungsi {name}(): Apapun {{ kembalikan {raw_code} }}"
    try:
        ast = _Helper.ast(code)
        _RUNTIME.Program(ast)
        func = _RUNTIME.current_scope.get(name)
        result = func() if func else None
        return repr(result)
    except Exception as error:
        raise except_maker(error, source=_highlight_source_line(raw_code))
    finally:
        COUNTER += 1

def _exec(code):
    try:
        ast = _Helper.ast(code)
        _RUNTIME.Program(ast)
    except Exception as e:
        src = "\n".join([_highlight_source_line(line) for line in code.splitlines()])
        raise except_maker(e, source=src)
