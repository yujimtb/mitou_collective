__all__ = ["SeedSummary", "seed_entropy_dataset"]


def __getattr__(name: str):
	if name in __all__:
		from app.seeds.entropy_dataset import SeedSummary, seed_entropy_dataset

		exports = {
			"SeedSummary": SeedSummary,
			"seed_entropy_dataset": seed_entropy_dataset,
		}
		return exports[name]
	raise AttributeError(f"module 'app.seeds' has no attribute {name!r}")