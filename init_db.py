from app.database import Base, engine
import app.models  # IMPORTANT : force l’enregistrement des tables

Base.metadata.create_all(bind=engine)
print("Tables créées avec succès")