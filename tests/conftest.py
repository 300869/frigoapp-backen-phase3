# tests/conftest.py
import os
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Utilise une base SQLite locale pour les tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

# Import de l'app FastAPI (package 'app' OU fichier 'main.py' à la racine)
try:
    from freshkeeper.main import freshkeeper  # app/main.py
except ModuleNotFoundError:
    from main import freshkeeper  # main.py à la racine


# -----------------------------
# Fixtures de test
# -----------------------------
@pytest.fixture(scope="session")
def client() -> TestClient:
    """Client HTTP pour les tests."""
    with TestClient(app) as c:
        yield c


# -----------------------------
# Helpers OpenAPI
# -----------------------------
def _pick_category_post_from_openapi(
    spec: Dict[str, Any],
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Dans l'OpenAPI, trouve un endpoint POST susceptible de créer une catégorie
    et retourne (path, request_body_schema_json) si trouvé.
    """
    paths = (spec or {}).get("paths", {}) or {}
    for path, methods in paths.items():
        post = (methods or {}).get("post")
        if not post:
            continue

        tags = [t.lower() for t in (post.get("tags") or [])]
        if ("categor" in path.lower()) or any("categor" in t for t in tags):
            rb = ((post.get("requestBody") or {}).get("content") or {}).get(
                "application/json"
            )
            if rb:  # on ne garde que ceux qui acceptent du JSON
                return path, rb
    return None


def _pick_categories_get_from_openapi(spec: Dict[str, Any]) -> Optional[str]:
    """
    Dans l'OpenAPI, trouve un endpoint GET listant les catégories.
    Retourne le path si trouvé.
    """
    paths = (spec or {}).get("paths", {}) or {}
    for path, methods in paths.items():
        get = (methods or {}).get("get")
        if not get:
            continue
        tags = [t.lower() for t in (get.get("tags") or [])]
        if ("categor" in path.lower()) or any("categor" in t for t in tags):
            return path
    return None


def _default_for(prop_schema: Dict[str, Any]) -> Any:
    """Valeur par défaut raisonnable pour un champ requis selon son type."""
    if "default" in prop_schema:
        return prop_schema["default"]

    typ = prop_schema.get("type")
    if typ == "string":
        return "Test"
    if typ == "integer":
        return 0
    if typ == "number":
        return 0
    if typ == "boolean":
        return True
    if typ == "array":
        return []
    if typ == "object":
        return {}
    return "Test"


def _build_payload_from_schema(body_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Construit une charge utile minimale à partir du schéma JSON OpenAPI."""
    schema = (body_schema or {}).get("schema", {}) or {}
    props: Dict[str, Any] = schema.get("properties") or {}  # type: ignore[assignment]
    required = schema.get("required") or []

    payload: Dict[str, Any] = {}
    if required:
        for name in required:
            payload[name] = _default_for(props.get(name, {}))
    else:
        for key in ("name", "title", "label"):
            if key in props:
                payload[key] = _default_for(props[key])
                break
        else:
            if props:
                first_key = next(iter(props))
                payload[first_key] = _default_for(props[first_key])
            else:
                payload["name"] = "Test"

    return payload


def _extract_id_from_response(
    data: Dict[str, Any], location_header: Optional[str]
) -> Optional[Any]:
    """Tente d'extraire un identifiant depuis différentes formes de réponse."""
    candidates = [
        data.get("id"),
        (data.get("category") or {}).get("id"),
        (data.get("data") or {}).get("id"),
        (data.get("result") or {}).get("id"),
    ]
    for cid in candidates:
        if cid is not None:
            return cid

    if location_header and "/" in location_header:
        try:
            return location_header.rstrip("/").split("/")[-1]
        except Exception:
            pass

    return None


def _list_categories(
    client: TestClient, fallback_paths: Optional[list] = None
) -> Tuple[str, Any]:
    """
    Récupère la liste des catégories en testant l'OpenAPI puis des fallbacks.
    Retourne (path_utilisé, json_réponse).
    """
    fallback_paths = fallback_paths or ["/categories", "/api/categories"]

    # Essaye via OpenAPI
    openapi = client.get("/openapi.json")
    if openapi.status_code == 200:
        spec = openapi.json()
        get_path = _pick_categories_get_from_openapi(spec)
        if get_path:
            r = client.get(get_path)
            if r.status_code == 200:
                return get_path, r.json()

    # Fallbacks connus
    for path in fallback_paths:
        r = client.get(path)
        if r.status_code == 200:
            return path, r.json()

    # Rien trouvé
    return "", None


def _find_category_id_in_listing(list_json: Any, wanted_name: str) -> Optional[Any]:
    """
    Essaie de retrouver l'id d'une catégorie au nom donné dans une liste JSON
    (quelle que soit sa structure courante).
    """
    if isinstance(list_json, dict):
        # Essais de structures communes
        for key in ("items", "results", "data", "categories"):
            if key in list_json and isinstance(list_json[key], list):
                for item in list_json[key]:
                    cid = _extract_id_from_response(item, None)
                    name = item.get("name") or item.get("title") or item.get("label")
                    if cid is not None and str(name) == wanted_name:
                        return cid
        # Peut-être que la liste est directement dans 'list_json'
        for v in list_json.values():
            if isinstance(v, list):
                for item in v:
                    if not isinstance(item, dict):
                        continue
                    cid = _extract_id_from_response(item, None)
                    name = item.get("name") or item.get("title") or item.get("label")
                    if cid is not None and str(name) == wanted_name:
                        return cid
    elif isinstance(list_json, list):
        for item in list_json:
            if not isinstance(item, dict):
                continue
            cid = _extract_id_from_response(item, None)
            name = item.get("name") or item.get("title") or item.get("label")
            if cid is not None and str(name) == wanted_name:
                return cid
    return None


# -----------------------------
# Fixture métier
# -----------------------------
@pytest.fixture
def category_id(client: TestClient):
    """
    Crée une catégorie de test. Si elle existe déjà, on réutilise son id.
    En dernier recours, on crée une catégorie au nom unique.
    """
    # 1) Récupérer l'OpenAPI
    openapi = client.get("/openapi.json")
    if openapi.status_code != 200:
        pytest.fail(
            f"Impossible de récupérer /openapi.json (status={openapi.status_code})"
        )
    spec = openapi.json()

    # 2) Sélectionner le POST de création des catégories
    picked = _pick_category_post_from_openapi(spec)
    if not picked:
        pytest.fail(
            "Aucun endpoint POST de création de catégorie trouvé dans l'OpenAPI."
        )
    path, body_schema = picked

    # 3) Construire la payload minimale valide (nom par défaut = "Test")
    payload = _build_payload_from_schema(body_schema)
    wanted_name = str(
        payload.get("name") or payload.get("title") or payload.get("label") or "Test"
    )

    # 4) Tenter la création
    resp = client.post(path, json=payload)
    if resp.status_code in (200, 201):
        data = resp.json()
        cid = _extract_id_from_response(
            data, resp.headers.get("Location") or resp.headers.get("location")
        )
        if cid is None:
            pytest.fail(f"Catégorie créée mais id introuvable dans la réponse: {data}")
        return cid

    # 5) Si 422 et message "existe déjà", on tente de récupérer son id via un GET
    if resp.status_code == 422:
        try:
            body = resp.json()
        except Exception:
            body = {"detail": str(resp.text)}

        detail_txt = str(body.get("detail", "")).lower()
        if (
            "existe déjà" in detail_txt
            or "already" in detail_txt
            or "exists" in detail_txt
        ):
            list_path, list_json = _list_categories(client)
            if list_json is not None:
                cid = _find_category_id_in_listing(list_json, wanted_name)
                if cid is not None:
                    return cid

            # Si on n'a pas retrouvé l'id, on crée une catégorie au nom unique
            unique_name = f"{wanted_name}-{uuid4().hex[:8]}"
            # remplace la clé correcte
            for k in ("name", "title", "label"):
                if k in payload:
                    payload[k] = unique_name
                    break
            else:
                payload["name"] = unique_name

            retry = client.post(path, json=payload)
            if retry.status_code in (200, 201):
                data = retry.json()
                cid = _extract_id_from_response(
                    data, retry.headers.get("Location") or retry.headers.get("location")
                )
                if cid is None:
                    pytest.fail(f"Catégorie créée (unique) mais id introuvable: {data}")
                return cid

            try:
                body2 = retry.json()
            except Exception:
                body2 = retry.text
            pytest.fail(
                f"Échec création catégorie unique sur {path} "
                f"(status={retry.status_code}, payload={payload}, body={body2})"
            )

    # 6) Autres erreurs : afficher le détail
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    pytest.fail(
        f"Création catégorie échouée sur {path} "
        f"(status={resp.status_code}, payload={payload}, body={body})"
    )
