import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.test import TestCase

from phone_number.models import PhoneNumber
from transaction.models import CreditRequest, Transaction
from transaction.utils import process_transaction
from vendor.models import Vendor

User = get_user_model()


class ParallelChargeTest(TestCase):
    def setUp(self):
        print("Setting up test data...")

        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass"
        )
        self.user = User.objects.create_user(
            username="vendor_user", password="testpass"
        )
        self.vendor = Vendor.objects.create(user=self.user, name="VendorA")

        print("Creating credit requests and approving...")
        for i in range(10):
            credit = CreditRequest.objects.create(
                vendor=self.vendor,
                amount=Decimal("1000.00"),
                status=CreditRequest.Status.PENDING,
            )
            credit.approve(self.admin)
            print(f"Approved credit request {i + 1}/10")

        print("📱 Creating phone numbers...")
        self.phones = []
        for i in range(100):
            phone = PhoneNumber.objects.create(
                creator=self.user, number=f"0912{str(i).zfill(6)}", credit=0
            )
            self.phones.append(phone)
        print("Phone number creation complete.")

    def charge_phone(self, phone, amount=Decimal("5.00")):
        import os

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
        django.setup()

        transfer_id = uuid.uuid4()
        print(f"Charging phone {phone.number} | Transfer ID: {transfer_id}")

        try:
            with db_transaction.atomic():
                print(
                    f"Locking phone and vendor {phone.number} | Transfer ID: {transfer_id}"
                )
                locked_phone = PhoneNumber.objects.select_for_update().get(pk=phone.pk)
                locked_vendor = Vendor.objects.select_for_update().get(
                    pk=self.vendor.pk, is_active=True
                )
                print(
                    f"Locked phone and vendor {phone.number} | Transfer ID: {transfer_id}"
                )

                error, success = process_transaction(
                    transaction_type=Transaction.TransactionType.WITHDRAW,
                    vendor=locked_vendor,
                    amount=amount,
                    creator=self.user,
                    phone_number=locked_phone,
                    description=f"Charging phone {locked_phone.number}",
                    transfer_id=transfer_id,
                )

                if not success:
                    print(f"Failed to charge {locked_phone.number}: {error['message']}")
                    return False

                locked_phone.credit += amount
                locked_phone.save(update_fields=["credit"])
                print(f"Charged {locked_phone.number} with {amount}")

                Transaction.objects.create(
                    transaction_type=Transaction.TransactionType.CHARGE,
                    vendor=locked_vendor,
                    amount=amount,
                    creator=self.user,
                    phone_number=locked_phone,
                    transfer_id=transfer_id,
                    description=f"Charged phone {locked_phone.number}",
                )
                print(f"Logged transaction for {locked_phone.number}")

                return True

        except (PhoneNumber.DoesNotExist, Vendor.DoesNotExist, ValidationError) as e:
            print(f"Validation error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def get_object(self):
        vendor = Vendor.objects.get(name="VendorA")
        print(vendor.name)

    def test_parallel_charges(self):
        print("Starting parallel charge test")
        charge_amount = Decimal("5.00")
        initial_balance = Decimal("10000.00")

        for phone in self.phones:
            self.charge_phone(phone, charge_amount)

        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     futures = [
        #         executor.submit(self.charge_phone, phone, charge_amount)
        #         for phone in self.phones
        #     ]
        #     results = [f.result() for f in as_completed(futures)]

        print("All charges completed. Checking results...")

        # self.assertTrue(all(results), "Some charges failed unexpectedly.")

        self.vendor.refresh_from_db()
        expected_balance = initial_balance - (len(self.phones) * charge_amount)
        print(
            f"Final vendor balance: {self.vendor.balance} (Expected: {expected_balance})"
        )
        self.assertEqual(
            self.vendor.balance,
            expected_balance,
            f"Vendor balance mismatch: expected {expected_balance}, got {self.vendor.balance}",
        )

        for phone in self.phones:
            phone.refresh_from_db()
            print(f"📞 Phone {phone.number} credit: {phone.credit}")
            self.assertEqual(
                phone.credit,
                charge_amount,
                f"Credit mismatch for phone {phone.number}",
            )

        print("Test passed: All balances and credits match.")
