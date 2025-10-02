import { IncomeStatementView } from "./income-statement-view";

import { getIncomeStatement } from "@/lib/api";
import { parseDate, toIsoDate } from "@/lib/utils";

export default async function IncomeStatementPage({
  searchParams,
}: {
  searchParams?: Record<string, string | string[] | undefined>;
}) {
  const params = searchParams ?? {};
  const now = new Date();
  const defaultStart = new Date(now.getFullYear(), 0, 1);
  const defaultEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const start = parseDate(typeof params.start_date === "string" ? params.start_date : undefined, defaultStart);
  const end = parseDate(typeof params.end_date === "string" ? params.end_date : undefined, defaultEnd);
  const cadenceParam = typeof params.cadence === "string" ? params.cadence : "monthly";
  const cadence = cadenceParam === "quarterly" ? "quarterly" : "monthly";
  const view = typeof params.view === "string" ? params.view : "summary";

  const data = await getIncomeStatement({
    startDate: toIsoDate(start),
    endDate: toIsoDate(end),
    cadence,
  });

  return (
    <IncomeStatementView
      data={data}
      startDateIso={toIsoDate(start)}
      endDateIso={toIsoDate(end)}
      cadence={cadence}
      view={view}
    />
  );
}
