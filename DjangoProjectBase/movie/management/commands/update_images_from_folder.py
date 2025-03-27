import os
import unicodedata
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie images in the database from the media folder"

    def normalize_title(self, title):
        """Normaliza el título eliminando prefijos, acentos y convirtiendo a minúsculas."""
        title = title.lower().strip()
        title_no_accents = ''.join(
            c for c in unicodedata.normalize('NFKD', title) if unicodedata.category(c) != 'Mn'
        )  # Mantiene caracteres pero sin acentos
        return title_no_accents

    def handle(self, *args, **kwargs):
        # 📂 Ruta de la carpeta donde están las imágenes
        images_folder = os.path.join(settings.MEDIA_ROOT, 'movie', 'images')

        if not os.path.exists(images_folder):
            self.stderr.write(f"Folder '{images_folder}' not found.")
            return

        updated_count = 0

        # 🔍 Recorremos los archivos en la carpeta
        for filename in os.listdir(images_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                movie_title, _ = os.path.splitext(filename)  # Extrae el nombre sin extensión
                
                # Versiones del título
                movie_title_original = movie_title.strip()  # Sin modificar
                movie_title_normalized = self.normalize_title(movie_title_original)  # Sin acentos
                movie_title_no_prefix = self.normalize_title(movie_title_original.replace('m_', '', 1))  # Sin 'm_'

                image_path = os.path.join('movie/images', filename)  # Ruta relativa desde MEDIA_ROOT

                try:
                    # 🔎 Buscar en la base de datos con diferentes variantes
                    movie = Movie.objects.filter(title__iexact=movie_title_original).first()
                    if not movie:
                        movie = Movie.objects.filter(title__iexact=movie_title_normalized).first()
                    if not movie:
                        movie = Movie.objects.filter(title__iexact=movie_title_no_prefix).first()

                    if movie:
                        movie.image = image_path
                        movie.save()
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
                    else:
                        self.stderr.write(f"Movie not found: {movie_title_original} (normalized: {movie_title_normalized}, no_prefix: {movie_title_no_prefix})")
                
                except Exception as e:
                    self.stderr.write(f"Failed to update {movie_title_original}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movie images."))
