from src.ingestion.generate_data import generate_data
from src.transformation.transform import run_transformations


def main():
    print("🚀 Starting pipeline...")

    generate_data()
    run_transformations()

    print("✅ Pipeline complete. Data is ready for Power BI.")


if __name__ == "__main__":
    main()