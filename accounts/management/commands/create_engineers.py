from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction

ENGINEER_CREDENTIALS = [
    ("upendra", "9390540794"),
    ("sivanambi", "111111111"),
    ("rishwanthr", "222222222"),
    ("gayadharm", "333333333"),
    ("eliyasp", "444444444"),
    ("narendrar", "555555555"),
    ("dilipm", "666666666"),
    ("yogananda", "777777777"),
    ("kunalm", "888888888"),
    ("rishwanthr2", "999999999")  # change if you have a 10th username
]

class Command(BaseCommand):
    help = "Create/ensure Engineer group and engineer users with provided passwords"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Engineer")
        created = updated = 0
        with transaction.atomic():
            for username, pwd in ENGINEER_CREDENTIALS:
                user, created_flag = User.objects.get_or_create(username=username)
                user.set_password(pwd)
                user.is_active = True
                user.is_staff = False
                user.save()
                user.groups.add(group)
                if created_flag:
                    created += 1
                else:
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Engineers processed. Created: {created}, Updated: {updated}"))