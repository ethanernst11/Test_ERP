from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Tuple

from django.db.models import Sum

from apps.ledger.models import Account, JournalEntry, JournalLine
from apps.invoicing.models import Invoice



@dataclass(frozen=True)
class Period:
    label: str
    start: date
    end: date


def _add_months(dt: date, months: int) -> date:
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def build_periods(start: date, end: date, cadence: str) -> List[Period]:
    if cadence not in {"monthly", "quarterly"}:
        raise ValueError("Cadence must be monthly or quarterly")
    periods: List[Period] = []
    cursor = start
    while cursor <= end:
        if cadence == "monthly":
            period_end = _add_months(cursor, 1) - timedelta(days=1)
            label = cursor.strftime("%b %Y")
            next_cursor = _add_months(cursor, 1)
        else:
            period_end = _add_months(cursor, 3) - timedelta(days=1)
            label = f"Q{((cursor.month - 1) // 3) + 1} {cursor.year}"
            next_cursor = _add_months(cursor, 3)
        if period_end > end:
            period_end = end
        periods.append(Period(label=label, start=cursor, end=period_end))
        cursor = next_cursor
    return periods


def _period_index(target: date, periods: List[Period]) -> int | None:
    for idx, period in enumerate(periods):
        if period.start <= target <= period.end:
            return idx
    return None


def _to_decimal(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    return value if isinstance(value, Decimal) else Decimal(str(value))


def trial_balance(start: date | None, end: date | None, account_ids: Iterable[int] | None = None) -> Dict[str, Any]:
    lines = JournalLine.objects.filter(entry__status=JournalEntry.Status.POSTED)
    if start:
        lines = lines.filter(entry__date__gte=start)
    if end:
        lines = lines.filter(entry__date__lte=end)
    if account_ids:
        lines = lines.filter(account_id__in=account_ids)

    aggregates = (
        lines
        .values("account_id", "account__code", "account__name")
        .annotate(total_debit=Sum("debit"), total_credit=Sum("credit"))
        .order_by("account__code")
    )

    rows: List[Dict[str, Any]] = []
    total_debits = Decimal("0")
    total_credits = Decimal("0")
    for item in aggregates:
        debit = _to_decimal(item["total_debit"])
        credit = _to_decimal(item["total_credit"])
        total_debits += debit
        total_credits += credit
        rows.append(
            {
                "account_id": item["account_id"],
                "code": item["account__code"],
                "name": item["account__name"],
                "debit": str(debit),
                "credit": str(credit),
            }
        )
    return {
        "rows": rows,
        "totals": {"debit": str(total_debits), "credit": str(total_credits)},
        "balanced": total_debits == total_credits,
    }


def income_statement(start: date, end: date, cadence: str = "monthly") -> Dict[str, Any]:
    periods = build_periods(start, end, cadence)
    account_queryset = Account.objects.filter(type__in=[Account.Type.REVENUE, Account.Type.EXPENSE]).select_related("parent")
    accounts = list(account_queryset)
    lines = (
        JournalLine.objects.filter(entry__status=JournalEntry.Status.POSTED, entry__date__gte=start, entry__date__lte=end)
        .select_related("entry", "account", "account__parent")
        .order_by("entry__date")
    )

    amounts: Dict[int, List[Decimal]] = {}
    for account in accounts:
        amounts[account.id] = [Decimal("0") for _ in periods]

    for line in lines:
        idx = _period_index(line.entry.date, periods)
        if idx is None:
            continue
        account = line.account
        if account.id not in amounts:
            # Ignore non P&L accounts that may appear on journal entries
            continue
        value = _to_decimal(line.debit) - _to_decimal(line.credit)
        if account.type == Account.Type.REVENUE:
            value = _to_decimal(line.credit) - _to_decimal(line.debit)
        amounts[account.id][idx] += value

    def classify_account(account: Account) -> str:
        if account.type == Account.Type.REVENUE:
            return "revenue"
        if account.code.startswith("5"):
            return "cogs"
        return "opex"

    groups = {
        "revenue": {"label": "REVENUE", "accounts": []},
        "cogs": {"label": "COGS", "accounts": []},
        "opex": {"label": "OPERATING EXPENSES", "accounts": []},
    }

    for account in accounts:
        group_key = classify_account(account)
        group = groups.get(group_key)
        if group is None:
            # Skip accounts that do not map into the predefined group buckets
            continue
        group["accounts"].append(account)

    def serialize_account(account: Account) -> Dict[str, Any]:
        values = amounts[account.id]
        return {
            "key": f"account-{account.id}",
            "label": f"{account.code} – {account.name}",
            "amounts": [str(v) for v in values],
            "total": str(sum(values, Decimal("0"))),
        }

    rows: List[Dict[str, Any]] = []
    flat_rows: List[Dict[str, Any]] = []

    def append_group(key: str):
        group = groups.get(key)
        if not group:
            length = len(periods)
            zeroes = [Decimal("0") for _ in range(length)]
            rows.append({
                "key": key,
                "label": key.replace("-", " ").upper(),
                "children": [],
                "amounts": [str(value) for value in zeroes],
                "total": "0",
            })
            flat_rows.append({"path": key.replace("-", " ").upper(), "amounts": ["0" for _ in range(length)], "total": "0"})
            return zeroes

        children_accounts = group["accounts"]
        if not children_accounts:
            length = len(periods)
            zeroes = [Decimal("0") for _ in range(length)]
            rows.append({
                "key": key,
                "label": group["label"],
                "children": [],
                "amounts": [str(value) for value in zeroes],
                "total": "0",
            })
            flat_rows.append({"path": group["label"], "amounts": ["0" for _ in range(length)], "total": "0"})
            return zeroes

        children = [serialize_account(acc) for acc in children_accounts]
        aggregates = [sum((amounts[acc.id][idx] for acc in children_accounts), Decimal("0")) for idx in range(len(periods))]
        group_row = {
            "key": key,
            "label": group["label"],
            "children": children,
            "amounts": [str(v) for v in aggregates],
            "total": str(sum(aggregates, Decimal("0"))),
        }
        rows.append(group_row)
        flat_rows.append({"path": group_row["label"], "amounts": group_row["amounts"], "total": group_row["total"]})
        for child in children:
            flat_rows.append({"path": f"{group_row['label']} > {child['label']}", "amounts": child["amounts"], "total": child["total"]})
        return aggregates

    revenue_totals = append_group("revenue")
    cogs_totals = append_group("cogs")
    opex_totals = append_group("opex")

    gross_profit = [rev - cogs for rev, cogs in zip(revenue_totals, cogs_totals)]
    net_income = [gp - opex for gp, opex in zip(gross_profit, opex_totals)]

    rows.insert(2, {
        "key": "gross-profit",
        "label": "GROSS PROFIT",
        "amounts": [str(v) for v in gross_profit],
        "total": str(sum(gross_profit, Decimal("0"))),
        "children": [],
    })
    flat_rows.append({"path": "GROSS PROFIT", "amounts": [str(v) for v in gross_profit], "total": str(sum(gross_profit, Decimal("0")))})

    rows.append({
        "key": "net-income",
        "label": "NET INCOME",
        "amounts": [str(v) for v in net_income],
        "total": str(sum(net_income, Decimal("0"))),
        "children": [],
    })
    flat_rows.append({"path": "NET INCOME", "amounts": [str(v) for v in net_income], "total": str(sum(net_income, Decimal("0")))})

    return {
        "periods": [period.label for period in periods],
        "period_meta": [
            {"label": period.label, "start": period.start.isoformat(), "end": period.end.isoformat()}
            for period in periods
        ],
        "rows": rows,
        "flat": flat_rows,
        "summary": {
            "gross_profit": [str(v) for v in gross_profit],
            "net_income": [str(v) for v in net_income],
        },
    }


def balance_sheet(as_of: date) -> Dict[str, Any]:
    lines = JournalLine.objects.filter(entry__status=JournalEntry.Status.POSTED, entry__date__lte=as_of)
    aggregates = (
        lines
        .values("account_id", "account__code", "account__name", "account__type")
        .annotate(total_debit=Sum("debit"), total_credit=Sum("credit"))
    )
    sections = defaultdict(list)
    totals = defaultdict(lambda: Decimal("0"))
    for item in aggregates:
        debit = _to_decimal(item["total_debit"])
        credit = _to_decimal(item["total_credit"])
        balance = debit - credit
        account_type = item["account__type"]
        if account_type in (Account.Type.REVENUE, Account.Type.EXPENSE):
            continue
        if account_type in (Account.Type.LIABILITY, Account.Type.EQUITY):
            balance = credit - debit
        sections[account_type].append(
            {
                "code": item["account__code"],
                "name": item["account__name"],
                "balance": str(balance),
            }
        )
        totals[account_type] += balance
    equity = totals[Account.Type.EQUITY]
    liabilities = totals[Account.Type.LIABILITY]
    assets = totals[Account.Type.ASSET]
    return {
        "as_of": as_of.isoformat(),
        "sections": {
            "assets": sections[Account.Type.ASSET],
            "liabilities": sections[Account.Type.LIABILITY],
            "equity": sections[Account.Type.EQUITY],
        },
        "totals": {
            "assets": str(assets),
            "liabilities_plus_equity": str(liabilities + equity),
        },
    }


def cash_flow(start: date, end: date) -> Dict[str, Any]:
    income = income_statement(start, end)
    net_income_total = sum(Decimal(value) for value in income["summary"]["net_income"]) if income["summary"].get("net_income") else Decimal("0")
    operating = net_income_total
    investing = Decimal("0")
    financing = Decimal("0")
    net_change = operating + investing + financing
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "sections": [
            {"label": "Net Income", "amount": str(net_income_total)},
            {"label": "Operating Activities", "amount": str(operating)},
            {"label": "Investing Activities", "amount": str(investing)},
            {"label": "Financing Activities", "amount": str(financing)},
        ],
        "net_change": str(net_change),
    }


def accounts_receivable_aging(reference_date: date | None = None) -> Dict[str, Any]:
    if reference_date is None:
        reference_date = date.today()

    buckets_config = [
        (0, 30, "0-30"),
        (31, 60, "31-60"),
        (61, 90, "61-90"),
        (91, 10_000, "90+"),
    ]

    summary: Dict[str, Dict[str, Any]] = {
        label: {"count": 0, "balance": Decimal("0")}
        for _, _, label in buckets_config
    }
    summary["Current"] = {"count": 0, "balance": Decimal("0")}

    rows: List[Dict[str, Any]] = []

    invoices = (
        Invoice.objects.select_related("customer")
        .order_by("due_date")
    )

    for invoice in invoices:
        balance = invoice.balance_due
        if balance <= 0:
            continue
        days_past_due = (reference_date - invoice.due_date).days
        if days_past_due < 0:
            bucket = "Current"
        else:
            bucket = "90+"
            for lower, upper, label in buckets_config:
                if lower <= days_past_due <= upper:
                    bucket = label
                    break

        summary.setdefault(bucket, {"count": 0, "balance": Decimal("0")})
        summary[bucket]["count"] += 1
        summary[bucket]["balance"] += balance

        rows.append(
            {
                "id": invoice.id,
                "number": invoice.number,
                "customer": invoice.customer.name,
                "balance": str(balance),
                "due_date": invoice.due_date.isoformat(),
                "days_past_due": max(days_past_due, 0),
                "bucket": bucket,
            }
        )

    formatted_summary = {
        label: {"count": data["count"], "balance": str(data["balance"])}
        for label, data in summary.items()
    }

    return {
        "reference_date": reference_date.isoformat(),
        "summary": formatted_summary,
        "rows": rows,
    }
