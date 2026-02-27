fix:
    ruff format .
    ruff check --fix .

fix-EXE002:
    ruff check --select 'EXE002' --output-format json . | jq '.[] | .filename' -r | xargs chmod -x

vm image="kanidm":
    nix run ".#{{ image }}"
