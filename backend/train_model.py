"""Train triage ML model from CSV."""

from backend.app.services.triage_ml import train_and_save

if __name__ == "__main__":
    pipeline = train_and_save()
    print(f"Model trained. Classes: {list(pipeline.classes_)}")
