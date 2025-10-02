from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role
from apps.approvals.models import Approval, CloseChecklistItem
from apps.budgets.models import Budget
from apps.ledger.models import Account, JournalEntry, JournalLine

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo ERP data including chart of accounts, journal entries, budgets, approvals, and users."

    def handle(self, *args, **options):
        with transaction.atomic():
            roles = self._ensure_roles()
            users = self._ensure_users(roles)
            accounts = self._ensure_accounts()
            self._seed_journal_entries(users["accountant"], users["admin"], accounts)
            self._seed_budgets(users["accountant"], accounts)
            self._seed_approvals(users["admin"], accounts)
            self._seed_checklist(users["accountant"])
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _ensure_roles(self) -> dict[str, Role]:
        role_map: dict[str, Role] = {}
        for code, name in Role.default_roles():
            role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
            role_map[code] = role
        return role_map

    def _ensure_users(self, roles: dict[str, Role]) -> dict[str, User]:
        users: dict[str, User] = {}
        user_specs = [
            ("admin", "Admin", "User", "admin@erp.local", [Role.Code.ADMIN]),
            ("accountant", "Alex", "Accountant", "accountant@erp.local", [Role.Code.ACCOUNTANT]),
            ("viewer", "Val", "Viewer", "viewer@erp.local", [Role.Code.VIEWER]),
        ]
        for username, first, last, email, role_codes in user_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                },
            )
            if created:
                user.set_password("changeme123")
                user.is_staff = Role.Code.ADMIN in role_codes
                user.save()
            roles_to_assign = Role.objects.filter(code__in=role_codes)
            user.erp_roles.set(roles_to_assign)
            users[username] = user
        return users

    def _ensure_accounts(self) -> dict[str, Account]:
        chart = [
            {"code": "1000", "name": "Cash", "type": Account.Type.ASSET},
            {"code": "1100", "name": "Accounts Receivable", "type": Account.Type.ASSET},
            {"code": "2000", "name": "Accounts Payable", "type": Account.Type.LIABILITY},
            {"code": "3000", "name": "Retained Earnings", "type": Account.Type.EQUITY},
            {"code": "4000", "name": "Product Revenue", "type": Account.Type.REVENUE},
            {"code": "5000", "name": "Cost of Goods Sold", "type": Account.Type.EXPENSE},
            {"code": "6000", "name": "Operating Expenses", "type": Account.Type.EXPENSE},
            {"code": "6100", "name": "Sales & Marketing", "type": Account.Type.EXPENSE, "parent": "6000"},
            {"code": "6200", "name": "Payroll", "type": Account.Type.EXPENSE, "parent": "6000"},
            {"code": "6300", "name": "Rent", "type": Account.Type.EXPENSE, "parent": "6000"},
        ]
        accounts: dict[str, Account] = {}
        for record in chart:
            parent = None
            if "parent" in record:
                parent_code = record.pop("parent")
                parent = Account.objects.filter(code=parent_code).first()
            account, _ = Account.objects.get_or_create(code=record["code"], defaults={
                "name": record["name"],
                "type": record["type"],
                "parent": parent,
            })
            if parent and account.parent_id != parent.id:
                account.parent = parent
                account.save(update_fields=["parent"])
            accounts[record["code"]] = account
        return accounts

    def _seed_journal_entries(self, accountant: User, approver: User, accounts: dict[str, Account]) -> None:
        current_year = timezone.now().date().year
        months = [date(current_year, month, 1) for month in range(1, 13)]
        revenue_base = Decimal("50000")
        cogs_ratio = Decimal("0.4")
        payroll = Decimal("15000")
        marketing = Decimal("8000")
        rent = Decimal("5000")

        for idx, first_day in enumerate(months, start=1):
            memo = f"Monthly close {first_day.strftime('%B %Y')}"
            entry, created = JournalEntry.objects.get_or_create(
                date=first_day,
                memo=memo,
                defaults={
                    "status": JournalEntry.Status.POSTED,
                    "created_by": accountant,
                    "approved_by": approver,
                },
            )
            if not created:
                continue
            revenue = revenue_base + Decimal(idx * 500)
            cogs = (revenue * cogs_ratio).quantize(Decimal("0.01"))
            total_expense = payroll + marketing + rent

            lines = [
                (accounts["1000"], revenue, Decimal("0")),
                (accounts["4000"], Decimal("0"), revenue),
                (accounts["5000"], cogs, Decimal("0")),
                (accounts["1000"], Decimal("0"), cogs),
                (accounts["6200"], payroll, Decimal("0")),
                (accounts["1000"], Decimal("0"), payroll),
                (accounts["6100"], marketing, Decimal("0")),
                (accounts["1000"], Decimal("0"), marketing),
                (accounts["6300"], rent, Decimal("0")),
                (accounts["1000"], Decimal("0"), rent),
            ]
            JournalLine.objects.bulk_create(
                [
                    JournalLine(
                        entry=entry,
                        account=account,
                        debit=debit,
                        credit=credit,
                        dimensions={"period": first_day.strftime("%Y-%m")},
                    )
                    for account, debit, credit in lines
                ]
            )

    def _seed_budgets(self, accountant: User, accounts: dict[str, Account]) -> None:
        year = timezone.now().date().year
        for month in range(1, 13):
            period_start = date(year, month, 1)
            if month == 12:
                period_end = date(year, 12, 31)
            else:
                period_end = date(year, month + 1, 1) - timedelta(days=1)
            Budget.objects.get_or_create(
                account=accounts["6100"],
                period_start=period_start,
                period_end=period_end,
                cadence=Budget.Cadence.MONTHLY,
                defaults={
                    "amount": Decimal("9000"),
                    "created_by": accountant,
                },
            )
            Budget.objects.get_or_create(
                account=accounts["6200"],
                period_start=period_start,
                period_end=period_end,
                cadence=Budget.Cadence.MONTHLY,
                defaults={
                    "amount": Decimal("16000"),
                    "created_by": accountant,
                },
            )

    def _seed_approvals(self, admin: User, accounts: dict[str, Account]) -> None:
        Approval.objects.get_or_create(
            object_type="journal_entry",
            object_id="latest",
            defaults={
                "status": Approval.Status.APPROVED,
                "actor": admin,
                "notes": "Initial revenue entries approved.",
            },
        )

    def _seed_checklist(self, owner: User) -> None:
        periods = ["Jan Close", "Feb Close", "Mar Close"]
        for period in periods:
            CloseChecklistItem.objects.get_or_create(
                name="Reconcile bank statements",
                period=period,
                defaults={
                    "status": CloseChecklistItem.Status.IN_PROGRESS,
                    "owner": owner,
                    "notes": "Imported from bank feed.",
                },
            )
            CloseChecklistItem.objects.get_or_create(
                name="Review revenue recognition",
                period=period,
                defaults={
                    "status": CloseChecklistItem.Status.PENDING,
                    "owner": owner,
                },
            )
