fix:
    ruff format .
    ruff check --fix .

fix-EXE002:
    ruff check --select 'EXE002' --output-format json . | jq '.[] | .filename' -r | xargs chmod -x

vm image="kanidm" *args="":
    nix run ".#{{ image }}" {{ args }}

fastapi:
    uvicorn aoidc.battery.fastapi.__main__:app --reload --port 9999

fetch-rfc:
    mkdir -p rfcs/
    for rfc in "rfc6749" "rfc7033" "rfc7591" "rfc7636" "rfc7662" "rfc8414"; do wget https://www.rfc-editor.org/rfc/$rfc.html -O ./rfcs/$rfc.html; done
    wget https://openid.net/specs/openid-connect-core-1_0-final.html -O ./rfcs/oidc_core.html; done
    wget https://openid.net/specs/openid-connect-discovery-1_0-final.html -O ./rfcs/oidc_discovery.html; done
