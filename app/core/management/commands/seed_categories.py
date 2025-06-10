from django.core.management.base import BaseCommand
from gear_hub.models import GearCategories

class Command(BaseCommand):
    help = 'Seed the database with initial categories and sub-categories'

    def handle(self, *args, **kwargs):
        categories = {
            "Audio": [
                "Amplifiers", "Audio Terminals", "Comms", "Microphones",
                "Mixers", "Mixers ENG", "Portable Digital Recorders",
                "Speakers", "Wireless"
            ],
            "Video": {
                "Cameras": ["Broadcast", "Cinema", "Photography"],
                "Lenses and Glass": ["Broadcast Glass", "Cine Glass", "Photography"],
                "Projectors": ["Under 10K", "Over 10K", "Projector Lenses"],
                "Switchers": ["Screen Management Switchers", "Broadcast Switchers and Fly Packs"],
                "Records": [],
                "Monitors": ["All Monitors", "Monitor Accessories"],
                "Computers": ["Apple", "PC"],
                "Video Accessories": ["Decimators", "Converters", "Adapters", "Misc"]
            },
            "Lighting": [],
            "Media Servers": [],
            "Scenic": ["Pipe & Drape", "Podiums", "Scenic Sets", "Misc"],
            "Power": [],
            "Rigging": ["Truss", "Motors"],
            "Expendables": [],
            "Fiber and Cable": [],
            "LED": ["Outdoor", "Indoor", "LED Processing"]
        }

        def create_category(name, parent=None):
            category, created = GearCategories.objects.get_or_create(category_name=name, parent=parent)
            return category

        for category_name, subcategories in categories.items():
            parent_category = create_category(category_name)

            if isinstance(subcategories, dict):
                for subcategory_name, sub_subcategories in subcategories.items():
                    subcategory = create_category(subcategory_name, parent=parent_category)
                    for sub_subcategory_name in sub_subcategories:
                        create_category(sub_subcategory_name, parent=subcategory)
            else:
                for subcategory_name in subcategories:
                    create_category(subcategory_name, parent=parent_category)

        self.stdout.write(self.style.SUCCESS('Successfully seeded categories and sub-categories'))
