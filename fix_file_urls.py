"""
Script to fix existing file URLs in database
Converts relative URLs (/uploads/...) to absolute URLs (https://domain.com/uploads/...)
"""
from app import create_app
from app.extensions import db
from app.models import Material

app = create_app()

with app.app_context():
    base_url = app.config.get('BASE_URL', 'https://kiaacdemy.pythonanywhere.com')

    # Get all materials with file URLs
    materials = Material.query.filter(Material.file_url.isnot(None)).all()

    updated_count = 0
    for material in materials:
        # Check if URL is relative
        if material.file_url and material.file_url.startswith('/uploads/'):
            # Convert to absolute URL
            material.file_url = f"{base_url}{material.file_url}"
            updated_count += 1
            print(f"Updated material {material.id}: {material.title}")

    # Commit changes
    if updated_count > 0:
        db.session.commit()
        print(f"\n✅ Updated {updated_count} material(s) with absolute URLs")
    else:
        print("ℹ️  No materials needed updating")
