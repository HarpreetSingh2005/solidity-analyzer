from solcx import compile_source, install_solc

install_solc("0.8.0")

def get_ast(source_code):
    compiled = compile_source(
        source_code,
        output_values=["ast"],
        solc_version="0.8.0"
    )

    _, contract_interface = compiled.popitem()
    return contract_interface["ast"]