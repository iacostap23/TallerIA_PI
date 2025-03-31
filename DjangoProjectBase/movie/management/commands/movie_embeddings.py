import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from movie.utils import get_embedding  

class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        for movie in movies:
            try:
                emb = get_embedding(movie.description)
                movie.emb = emb.tobytes()
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding almacenado para: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"❌ Error en {movie.title}: {e}")
