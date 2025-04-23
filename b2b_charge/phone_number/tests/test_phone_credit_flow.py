from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

from vendor.models import Vendor
from phone_number.models import PhoneNumber
from transaction.models import Transaction, CreditRequest
from transaction.utils import process_transaction

User = get_user_model()


class VendorPhoneCreditFlowTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass"
        )
        self.vendors = []

        for i in range(2):
            user = User.objects.create_user(
                username=f"vendor_user{i}", password="testpass"
            )
            vendor = Vendor.objects.create(user=user, name=f"Vendor{i}")
            self.vendors.append((vendor, user))

            # Submit 10 credit requests of 1000 each and approve them
            for _ in range(10):
                credit_req = CreditRequest.objects.create(
                    vendor=vendor,
                    amount=Decimal("1000.00"),
                    status=CreditRequest.Status.PENDING,
                )
                credit_req.approve(self.admin)

        # Create 1000 phones per vendor.user
        self.phone_map = {}
        for vendor, user in self.vendors:
            self.phone_map[user.id] = []
            for j in range(1000):
                phone = PhoneNumber.objects.create(
                    creator=user, number=f"09{user.id}{j:08d}", credit=0
                )
                self.phone_map[user.id].append(phone)

    def test_charging_phones_and_vendor_balances(self):
        charge_amount = Decimal("5.00")

        for vendor, user in self.vendors:
            for phone in self.phone_map[user.id]:
                transfer_id = uuid.uuid4()

                # Withdraw from vendor
                error, success = process_transaction(
                    transaction_type=Transaction.TransactionType.WITHDRAW,
                    vendor=vendor,
                    amount=charge_amount,
                    creator=user,
                    description=f"Charging phone {phone.number}",
                    transfer_id=transfer_id,
                )
                self.assertTrue(success, msg=f"Withdraw failed: {error['message']}")

                # Credit the phone
                phone.credit += charge_amount
                phone.save()

                # Log CHARGE transaction
                Transaction.objects.create(
                    transaction_type=Transaction.TransactionType.CHARGE,
                    vendor=vendor,
                    amount=charge_amount,
                    creator=user,
                    phone_number=phone,
                    transfer_id=transfer_id,
                    description=f"Charged phone {phone.number}",
                )

            # Check vendor balance
            vendor.refresh_from_db()
            expected_balance = Decimal("10000.00") - (1000 * charge_amount)
            self.assertEqual(
                vendor.balance, expected_balance, msg=f"{vendor.name} balance mismatch"
            )

            # Check phone credits
            for phone in self.phone_map[user.id]:
                phone.refresh_from_db()
                self.assertEqual(
                    phone.credit, charge_amount, msg=f"{phone.number} credit mismatch"
                )
