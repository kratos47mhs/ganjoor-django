"""
Management command to import Ganjoor data from CSV files.

This command imports poets, categories, poems, and verses from CSV files
into the database.
"""

import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import GanjoorPoet, GanjoorCategory, GanjoorPoem, GanjoorVerse

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import Ganjoor data from CSV files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--poets",
            type=str,
            help="Path to poets.csv file",
        )
        parser.add_argument(
            "--cats",
            type=str,
            help="Path to categories.csv file",
        )
        parser.add_argument(
            "--poems",
            type=str,
            help="Path to poems.csv file",
        )
        parser.add_argument(
            "--verses",
            type=str,
            help="Path to verses.csv file",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to import in each batch (default: 1000)",
        )

    def handle(self, *args, **options):
        """Main handler for the import command."""
        if not any(
            [options["poets"], options["cats"], options["poems"], options["verses"]]
        ):
            raise CommandError(
                "At least one CSV file must be specified. "
                "Use --poets, --cats, --poems, or --verses"
            )

        batch_size = options["batch_size"]

        if options["poets"]:
            self.import_poets(options["poets"], batch_size)

        if options["cats"]:
            self.import_categories(options["cats"], batch_size)

        if options["poems"]:
            self.import_poems(options["poems"], batch_size)

        if options["verses"]:
            self.import_verses(options["verses"], batch_size)

        self.stdout.write(self.style.SUCCESS("✓ Import completed successfully!"))

    @transaction.atomic
    def import_poets(self, path, batch_size):
        """
        Import poets from CSV file.

        Expected CSV columns: Id, Name, Description (optional), Century (optional)
        """
        self.stdout.write(f"Importing poets from {path}...")

        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                poets_to_create = []
                count = 0
                skipped = 0

                for row in reader:
                    poet_id = row.get("Id")
                    name = row.get("Name", "").strip()

                    if not poet_id or not name:
                        skipped += 1
                        logger.warning(f"Skipping invalid poet row: {row}")
                        continue

                    # Check if poet already exists
                    if GanjoorPoet.objects.filter(id=poet_id).exists():
                        skipped += 1
                        continue

                    poet = GanjoorPoet(
                        id=int(poet_id),
                        name=name,
                        description=row.get("Description", "").strip(),
                        century=row.get("Century", "classical").strip(),
                    )
                    poets_to_create.append(poet)
                    count += 1

                    # Bulk create in batches
                    if len(poets_to_create) >= batch_size:
                        GanjoorPoet.objects.bulk_create(
                            poets_to_create, ignore_conflicts=True
                        )
                        self.stdout.write(f"  Imported {count} poets...")
                        poets_to_create = []

                # Import remaining poets
                if poets_to_create:
                    GanjoorPoet.objects.bulk_create(
                        poets_to_create, ignore_conflicts=True
                    )

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {count} poets ({skipped} skipped)")
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except Exception as e:
            raise CommandError(f"Error importing poets: {e}")

    @transaction.atomic
    def import_categories(self, path, batch_size):
        """
        Import categories from CSV file.

        Expected CSV columns: Id, PoetId, ParentId (nullable), Title, Url (optional)
        """
        self.stdout.write(f"Importing categories from {path}...")

        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Read all rows first (need two passes for parent relationships)
                all_rows = list(reader)

                # First pass: create categories without parent
                categories_to_create = []
                count = 0
                skipped = 0

                for row in all_rows:
                    cat_id = row.get("Id")
                    poet_id = row.get("PoetId")
                    title = row.get("Title", "").strip()

                    if not cat_id or not poet_id or not title:
                        skipped += 1
                        logger.warning(f"Skipping invalid category row: {row}")
                        continue

                    # Check if category already exists
                    if GanjoorCategory.objects.filter(id=cat_id).exists():
                        skipped += 1
                        continue

                    # Check if poet exists
                    try:
                        poet = GanjoorPoet.objects.get(id=int(poet_id))
                    except GanjoorPoet.DoesNotExist:
                        skipped += 1
                        logger.warning(
                            f"Poet {poet_id} not found for category {cat_id}"
                        )
                        continue

                    category = GanjoorCategory(
                        id=int(cat_id),
                        poet=poet,
                        title=title,
                        url=row.get("Url", "").strip(),
                        parent=None,  # Set parent in second pass
                    )
                    categories_to_create.append(category)
                    count += 1

                    if len(categories_to_create) >= batch_size:
                        GanjoorCategory.objects.bulk_create(
                            categories_to_create, ignore_conflicts=True
                        )
                        self.stdout.write(f"  Imported {count} categories...")
                        categories_to_create = []

                if categories_to_create:
                    GanjoorCategory.objects.bulk_create(
                        categories_to_create, ignore_conflicts=True
                    )

                # Second pass: set parent relationships
                self.stdout.write("  Setting parent relationships...")
                parent_updates = 0

                for row in all_rows:
                    cat_id = row.get("Id")
                    parent_id = row.get("ParentId")

                    if not parent_id or parent_id == "0" or parent_id == "":
                        continue

                    try:
                        category = GanjoorCategory.objects.get(id=int(cat_id))
                        parent = GanjoorCategory.objects.get(id=int(parent_id))
                        category.parent = parent
                        category.save(update_fields=["parent"])
                        parent_updates += 1
                    except (GanjoorCategory.DoesNotExist, ValueError):
                        logger.warning(
                            f"Could not set parent {parent_id} for category {cat_id}"
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Imported {count} categories ({skipped} skipped, "
                        f"{parent_updates} parent relationships set)"
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except Exception as e:
            raise CommandError(f"Error importing categories: {e}")

    @transaction.atomic
    def import_poems(self, path, batch_size):
        """
        Import poems from CSV file.

        Expected CSV columns: Id, CatId, Title, Url
        """
        self.stdout.write(f"Importing poems from {path}...")

        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                poems_to_create = []
                count = 0
                skipped = 0

                for row in reader:
                    poem_id = row.get("Id")
                    cat_id = row.get("CatId")
                    title = row.get("Title", "").strip()

                    if not poem_id or not cat_id or not title:
                        skipped += 1
                        logger.warning(f"Skipping invalid poem row: {row}")
                        continue

                    # Check if poem already exists
                    if GanjoorPoem.objects.filter(id=poem_id).exists():
                        skipped += 1
                        continue

                    # Check if category exists
                    try:
                        category = GanjoorCategory.objects.get(id=int(cat_id))
                    except GanjoorCategory.DoesNotExist:
                        skipped += 1
                        logger.warning(
                            f"Category {cat_id} not found for poem {poem_id}"
                        )
                        continue

                    poem = GanjoorPoem(
                        id=int(poem_id),
                        category=category,
                        title=title,
                        url=row.get("Url", "").strip(),
                    )
                    poems_to_create.append(poem)
                    count += 1

                    if len(poems_to_create) >= batch_size:
                        GanjoorPoem.objects.bulk_create(
                            poems_to_create, ignore_conflicts=True
                        )
                        self.stdout.write(f"  Imported {count} poems...")
                        poems_to_create = []

                if poems_to_create:
                    GanjoorPoem.objects.bulk_create(
                        poems_to_create, ignore_conflicts=True
                    )

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {count} poems ({skipped} skipped)")
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except Exception as e:
            raise CommandError(f"Error importing poems: {e}")

    @transaction.atomic
    def import_verses(self, path, batch_size):
        """
        Import verses from CSV file.

        Expected CSV columns: Id, PoemId, VOrder, Position, Text
        """
        self.stdout.write(f"Importing verses from {path}...")

        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                verses_to_create = []
                count = 0
                skipped = 0

                for row in reader:
                    verse_id = row.get("Id")
                    poem_id = row.get("PoemId")
                    text = row.get("Text", "").strip()
                    order = row.get("VOrder")
                    position = row.get("Position", "0")

                    if not verse_id or not poem_id or not text or order is None:
                        skipped += 1
                        logger.warning(f"Skipping invalid verse row: {row}")
                        continue

                    # Check if verse already exists
                    if GanjoorVerse.objects.filter(id=verse_id).exists():
                        skipped += 1
                        continue

                    # Check if poem exists
                    try:
                        poem = GanjoorPoem.objects.get(id=int(poem_id))
                    except GanjoorPoem.DoesNotExist:
                        skipped += 1
                        logger.warning(f"Poem {poem_id} not found for verse {verse_id}")
                        continue

                    verse = GanjoorVerse(
                        id=int(verse_id),
                        poem=poem,
                        text=text,
                        order=int(order),
                        position=int(position),
                    )
                    verses_to_create.append(verse)
                    count += 1

                    if len(verses_to_create) >= batch_size:
                        GanjoorVerse.objects.bulk_create(
                            verses_to_create, ignore_conflicts=True
                        )
                        self.stdout.write(f"  Imported {count} verses...")
                        verses_to_create = []

                if verses_to_create:
                    GanjoorVerse.objects.bulk_create(
                        verses_to_create, ignore_conflicts=True
                    )

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {count} verses ({skipped} skipped)")
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except Exception as e:
            raise CommandError(f"Error importing verses: {e}")
