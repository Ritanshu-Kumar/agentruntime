from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_exists():
    dockerfile = ROOT / "Dockerfile"

    assert dockerfile.exists()


def test_compose_contains_api_and_postgres():
    compose = ROOT / "docker-compose.yml"

    content = compose.read_text()

    assert "postgres:" in content
    assert "api:" in content
    assert "postgres_data:" in content


def test_postgres_has_healthcheck():
    compose = ROOT / "docker-compose.yml"

    content = compose.read_text()

    assert "healthcheck:" in content
    assert "pg_isready" in content


def test_api_waits_for_postgres():
    compose = ROOT / "docker-compose.yml"

    content = compose.read_text()

    assert "condition: service_healthy" in content