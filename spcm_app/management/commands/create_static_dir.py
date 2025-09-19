"""
Django management command to create required directories
Usage: python manage.py create_static_dir
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Create required static and media directories'

    def handle(self, *args, **options):
        # Create static directory
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created static directory: {static_dir}')
            )
        else:
            self.stdout.write(f'Static directory already exists: {static_dir}')
        
        # Create media directory
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created media directory: {media_dir}')
            )
        else:
            self.stdout.write(f'Media directory already exists: {media_dir}')
        
        # Create templates directory
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created templates directory: {templates_dir}')
            )
        else:
            self.stdout.write(f'Templates directory already exists: {templates_dir}')
        
        self.stdout.write(
            self.style.SUCCESS('✅ All required directories created successfully!')
        )
