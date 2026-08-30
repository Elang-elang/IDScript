from src.IDScript import Compile

compiler = Compile(
    file_path=__file__,
    code=open('./example.ids').read(),
    module=False
)
compiler.run()