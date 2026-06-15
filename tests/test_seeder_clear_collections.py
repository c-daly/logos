"""seeder.clear() must preserve the Milvus collections unless explicitly asked
to drop them (logos#559 — a #515 regression broke seamless reseed)."""

from unittest.mock import MagicMock, patch

from logos_hcg.seeder import HCGSeeder


def test_clear_preserves_collections_by_default():
    seeder = HCGSeeder(MagicMock())
    with (
        patch.object(seeder, "_clear_redis_ontology"),
        patch.object(HCGSeeder, "_clear_milvus_collections") as drop,
    ):
        seeder.clear()
    drop.assert_not_called()  # collections kept (loaded) -> seamless reseed
    seeder.client.clear_all.assert_called_once()


def test_clear_drops_collections_when_requested():
    seeder = HCGSeeder(MagicMock())
    with (
        patch.object(seeder, "_clear_redis_ontology"),
        patch.object(HCGSeeder, "_clear_milvus_collections") as drop,
    ):
        seeder.clear(drop_collections=True)  # embedding-type change only
    drop.assert_called_once()
