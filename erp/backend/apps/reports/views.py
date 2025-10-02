from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    BalanceSheetQuerySerializer,
    CashFlowQuerySerializer,
    DateRangeSerializer,
    IncomeStatementQuerySerializer,
)
from .services import balance_sheet, cash_flow, income_statement, trial_balance


class TrialBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = DateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data.get("start_date")
        end = serializer.validated_data.get("end_date")
        account_ids = request.query_params.getlist("account")
        account_ids = [int(value) for value in account_ids if value.isdigit()]
        data = trial_balance(start, end, account_ids or None)
        return Response(data)


class IncomeStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = IncomeStatementQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = income_statement(
            serializer.validated_data["start_date"],
            serializer.validated_data["end_date"],
            serializer.validated_data["cadence"],
        )
        return Response(data)


class BalanceSheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = BalanceSheetQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = balance_sheet(serializer.validated_data["as_of"])
        return Response(data)


class CashFlowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CashFlowQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = cash_flow(
            serializer.validated_data["start_date"],
            serializer.validated_data["end_date"],
        )
        return Response(data)
