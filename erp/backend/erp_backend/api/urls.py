from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.viewsets import AuthViewSet, RoleViewSet, UserViewSet
from apps.ledger.viewsets import AccountViewSet, JournalEntryViewSet
from apps.budgets.viewsets import BudgetViewSet
from apps.approvals.viewsets import ApprovalViewSet, CloseChecklistItemViewSet
from apps.invoicing.viewsets import CustomerViewSet, InvoiceViewSet, PaymentViewSet
from apps.reports.views import (
    BalanceSheetView,
    CashFlowView,
    IncomeStatementView,
    TrialBalanceView,
    AccountsReceivableAgingView,
)

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"journal-entries", JournalEntryViewSet, basename="journalentry")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"approvals", ApprovalViewSet, basename="approval")
router.register(r"close-checklist", CloseChecklistItemViewSet, basename="closechecklist")
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", AuthViewSet.as_view({"post": "login"}), name="auth-login"),
    path("auth/logout/", AuthViewSet.as_view({"post": "logout"}), name="auth-logout"),
    path("me/", AuthViewSet.as_view({"get": "current_user"}), name="auth-me"),
    path("reports/trial-balance/", TrialBalanceView.as_view(), name="reports-trial-balance"),
    path("reports/income-statement/", IncomeStatementView.as_view(), name="reports-income-statement"),
    path("reports/balance-sheet/", BalanceSheetView.as_view(), name="reports-balance-sheet"),
    path("reports/cash-flow/", CashFlowView.as_view(), name="reports-cash-flow"),
    path("reports/ar-aging/", AccountsReceivableAgingView.as_view(), name="reports-ar-aging"),
]
