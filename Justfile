fix:
    ruff format .
    ruff check --fix .

fix-EXE002:
    ruff check --select 'EXE002' --output-format json . | jq '.[] | .filename' -r | xargs chmod -x

vm image="kanidm" *args="":
    nix run ".#{{ image }}" {{ args }}

fastapi:
    uvicorn aoidc.battery.fastapi.__main__:app --reload --port 9999
