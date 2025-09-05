import csv
from django.core.management.base import BaseCommand
from core.models import GanjoorPoet, GanjoorCat, GanjoorPoem, GanjoorVerse


class Command(BaseCommand):
    help = "Import Ganjoor data from CSV files"

    def add_arguments(self, parser):
        parser.add_argument("--poets", type=str, help="Path to poets.csv")
        parser.add_argument("--cats", type=str, help="Path to cats.csv")
        parser.add_argument("--poems", type=str, help="Path to poems.csv")
        parser.add_argument("--verses", type=str, help="Path to verses.csv")

    def handle(self, *args, **options):
        if options["poets"]:
            self.import_poets(options["poets"])
        if options["cats"]:
            self.import_cats(options["cats"])
        if options["poems"]:
            self.import_poems(options["poems"])
        if options["verses"]:
            self.import_verses(options["verses"])

    def import_poets(self, path):
        self.stdout.write(f"Importing poets from {path}")
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                GanjoorPoet.objects.get_or_create(
                    id=row["Id"],
                    defaults={"name": row["Name"], "slug": row["Slug"]},
                )

    def import_cats(self, path):
        self.stdout.write(f"Importing categories from {path}")
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                poet = GanjoorPoet.objects.get(id=row["PoetId"])
                parent = GanjoorCat.objects.filter(id=row["ParentId"]).first()
                GanjoorCat.objects.get_or_create(
                    id=row["Id"],
                    defaults={
                        "poet": poet,
                        "parent": parent,
                        "text": row["Text"],
                        "slug": row["Slug"],
                    },
                )

    def import_poems(self, path):
        self.stdout.write(f"Importing poems from {path}")
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                category = GanjoorCat.objects.get(id=row["CatId"])
                GanjoorPoem.objects.get_or_create(
                    id=row["Id"],
                    defaults={
                        "category": category,
                        "title": row["Title"],
                        "slug": row["Slug"],
                        "url": row["Url"],
                        "full_url": row.get("FullUrl", ""),
                    },
                )

    def import_verses(self, path):
        self.stdout.write(f"Importing verses from {path}")
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                poem = GanjoorPoem.objects.get(id=row["PoemId"])
                GanjoorVerse.objects.get_or_create(
                    id=row["Id"],
                    defaults={
                        "poem": poem,
                        "text": row["Text"],
                        "order": row["VOrder"],
                        "position": row["Position"],
                    },
                )
