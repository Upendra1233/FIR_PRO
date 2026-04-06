import pandas as pd
from io import BytesIO
from datetime import date, timedelta, datetime, time
from direct_calls.models import DirectCall
from django.core.mail import EmailMessage
from django.utils import timezone
import string
import re
import warnings

def get_call_status_report(call_type='Direct Call'):
    today = date.today()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    # build datetime range (use timezone-aware datetimes when possible)
    start_of_month = datetime.combine(month_start, time.min)
    end_of_today = datetime.combine(today, time.max)
    try:
        tz = timezone.get_current_timezone()
        start_of_month = timezone.make_aware(start_of_month, tz)
        end_of_today = timezone.make_aware(end_of_today, tz)
    except Exception:
        # fall back to naive datetimes if timezone conversion fails
        pass

    # Get unique engineers for the month
    month_qs = DirectCall.objects.filter(
        call_type=call_type,
        date_of_complaint__gte=start_of_month,
        date_of_complaint__lte=end_of_today,
    )
    engineers = (
        month_qs.exclude(complaint_assigned_to__isnull=True)
        .exclude(complaint_assigned_to__exact='')
        .values_list('complaint_assigned_to', flat=True)
        .distinct()
    )

    # Define the fixed status order required by the report (Day then Month)
    status_order = [
        'Resolved',
        'Closed',
        'FIR-Replace_Repair',
        'FIR-Replace',
        'FIR-Repair',
        'FIR-For Approval',
        'Cancelled',
        'Hold',
        'Closed-CI',
        'Pending',
    ]

    # Build HTML header in the exact order requested:
    header = """
    <tr>
        <th>Complaint assigned to</th>
        <th>{call_type} Attended<br>For the Day (yesterday)</th>
    """.format(call_type=call_type)

    for s in status_order:
        header += f"<th>{s} (Day)</th>"

    # Place Total Resolved and % BEFORE Day Feedback
    header += "<th>Total Resolved (C+D) (Day)</th><th>% of resolution (Day)</th>"
    header += "<th>Feed Back form Received (Day)</th>"

    header += f"<th>{call_type} Attended<br>For the Month</th>"

    for s in status_order:
        header += f"<th>{s} (Month)</th>"

    # Place Total Resolved and % BEFORE Month Feedback
    header += "<th>Total Resolved (C+D) (Month)</th><th>% of resolution (Month)</th>"
    header += "<th>Feed Back form Received (Month)</th>"

    header += """
    </tr>
    """

    report_rows = []

    # Totals (separate day/month feedback totals)
    total_day = total_month = 0
    total_resolved_day = total_resolved_month = 0
    total_closed = total_cancelled = total_d1 = total_d2 = total_d3 = 0
    total_feedback_day = 0
    total_feedback_month = 0
    total_status_day = {s: 0 for s in status_order}
    total_status_month = {s: 0 for s in status_order}

    for eng in engineers:
        # For the day (yesterday)
        start_of_day = datetime.combine(yesterday, time.min)
        end_of_day = datetime.combine(yesterday, time.max)
        try:
            tz = timezone.get_current_timezone()
            start_of_day = timezone.make_aware(start_of_day, tz)
            end_of_day = timezone.make_aware(end_of_day, tz)
        except Exception:
            pass

        calls_day = DirectCall.objects.filter(
            complaint_assigned_to__iexact=eng,
            call_type=call_type,
            date_of_complaint__gte=start_of_day,
            date_of_complaint__lte=end_of_day,
        )
        direct_calls_day = calls_day.count()

        # Day status counts using the fixed order
        status_day_counts = {s: calls_day.filter(call_status=s).count() for s in status_order}

        # Day feedback count (after Pending)
        feedback_day = calls_day.exclude(feedback__isnull=True).exclude(feedback='').count()

        # Day resolved (C+D definition applied to day)
        resolved_day = calls_day.filter(call_status__in=[
            'Resolved', 'FIR-Replace_Repair', 'FIR-Replace', 'FIR-Repair', 'FIR-For Approval'
        ]).count()
        percent_resolution_day = f"{(resolved_day / direct_calls_day * 100):.1f}%" if direct_calls_day else "0%"

        # For the month
        calls_month = DirectCall.objects.filter(
            complaint_assigned_to__iexact=eng,
            call_type=call_type,
            date_of_complaint__gte=start_of_month,
            date_of_complaint__lte=end_of_today
        )
        direct_calls_month = calls_month.count()

        # Month status counts using the fixed order
        status_month_counts = {s: calls_month.filter(call_status=s).count() for s in status_order}

        # Month feedback
        feedback_month = calls_month.exclude(feedback__isnull=True).exclude(feedback='').count()

        # Resolved definition (C+D) for month
        resolved_month = calls_month.filter(call_status__in=[
            'Resolved', 'FIR-Replace_Repair', 'FIR-Replace', 'FIR-Repair', 'FIR-For Approval'
        ]).count()

        percent_resolution_month = f"{(resolved_month / direct_calls_month * 100):.1f}%" if direct_calls_month else "0%"

        # Totals accumulation
        total_day += direct_calls_day
        total_month += direct_calls_month
        total_resolved_day += resolved_day
        total_resolved_month += resolved_month
        total_feedback_day += feedback_day
        total_feedback_month += feedback_month
        # keep old totals for compatibility (closed/cancelled/d1..d3)
        total_closed += calls_month.filter(call_status='Closed').count()
        total_cancelled += calls_month.filter(call_status='Cancelled').count()
        total_d1 += calls_month.filter(call_status='D1 Done').count()
        total_d2 += calls_month.filter(call_status='D2 Done').count()
        total_d3 += calls_month.filter(call_status='D3 Done').count()

        for s in status_order:
            total_status_day[s] += status_day_counts[s]
            total_status_month[s] += status_month_counts[s]

        # Build row in requested order:
        row = f"<tr><td>{eng}</td><td>{direct_calls_day}</td>"
        # Day statuses in order
        for s in status_order:
            row += f"<td>{status_day_counts[s]}</td>"
        # Day resolved & percent BEFORE Day feedback
        row += f"<td>{resolved_day}</td><td>{percent_resolution_day}</td>"
        # Day feedback
        row += f"<td>{feedback_day}</td>"

        # Month attended and month statuses
        row += f"<td>{direct_calls_month}</td>"
        for s in status_order:
            row += f"<td>{status_month_counts[s]}</td>"
        # Month resolved & percent BEFORE Month feedback
        row += f"<td>{resolved_month}</td><td>{percent_resolution_month}</td>"
        # Month feedback
        row += f"<td>{feedback_month}</td>"

        row += "</tr>"

        report_rows.append(row)

    # Totals row - follow the same column order as header
    percent_day_total = f"{(total_resolved_day / total_day * 100):.1f}%" if total_day else "0%"
    percent_month_total = f"{(total_resolved_month / total_month * 100):.1f}%" if total_month else "0%"

    total_row = f"<tr style='font-weight:bold;background:#eee;'><td>Total</td><td>{total_day}</td>"
    for s in status_order:
        total_row += f"<td>{total_status_day[s]}</td>"
    total_row += f"<td>{total_resolved_day}</td><td>{percent_day_total}</td>"
    total_row += f"<td>{total_feedback_day}</td>"
    total_row += f"<td>{total_month}</td>"
    for s in status_order:
        total_row += f"<td>{total_status_month[s]}</td>"
    total_row += f"<td>{total_resolved_month}</td><td>{percent_month_total}</td>"
    total_row += f"<td>{total_feedback_month}</td></tr>"

    report_rows.append(total_row)

    html_table = f"""
    <h3>Call Type : {call_type} Status</h3>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;width:100%;">
        <thead style="background:#d9edf7;">
            {header}
        </thead>
        <tbody>
            {''.join(report_rows)}
        </tbody>
    </table>
    """
    return html_table

def send_combined_status_report():
    today = date.today()
    month_start = today.replace(day=1)
    # build datetime range for attachments/export
    start_of_month = datetime.combine(month_start, time.min)
    end_of_today = datetime.combine(today, time.max)
    try:
        tz = timezone.get_current_timezone()
        start_of_month = timezone.make_aware(start_of_month, tz)
        end_of_today = timezone.make_aware(end_of_today, tz)
    except Exception:
        pass

    # Prepare HTML tables
    direct_call_table = get_call_status_report('Direct Call')
    ialert_call_table = get_call_status_report('I Alert Call')

    # Prepare Excel attachment for current month raw data
    qs = DirectCall.objects.filter(date_of_complaint__gte=start_of_month, date_of_complaint__lte=end_of_today)
    # Convert queryset to DataFrame
    df = pd.DataFrame(list(qs.values()))

    # Make only the model's date/datetime columns timezone-unaware (safe)
    from pandas.api import types as ptypes
    from django.db.models import DateField, DateTimeField

    model_date_fields = [
        f.name for f in DirectCall._meta.get_fields()
        if isinstance(f, (DateField, DateTimeField))
    ]

    for fname in model_date_fields:
        if fname not in df.columns:
            continue
        try:
            ser = df[fname]
            # tz-aware dtype -> convert to UTC and drop tz
            if ptypes.is_datetime64tz_dtype(ser.dtype):
                df[fname] = ser.dt.tz_convert('UTC').dt.tz_localize(None)
                continue
            # datetime64 dtype -> normalize/coerce
            if ptypes.is_datetime64_any_dtype(ser.dtype):
                df[fname] = pd.to_datetime(ser, errors='coerce')
                continue
            # object dtype -> try parsing only for these known date fields
            if ser.dtype == object:
                parsed = pd.to_datetime(ser, errors='coerce', utc=True)
                if ptypes.is_datetime64tz_dtype(parsed.dtype):
                    df[fname] = parsed.dt.tz_convert('UTC').dt.tz_localize(None)
                else:
                    df[fname] = parsed
        except Exception:
            # keep original as string on failure
            try:
                df[fname] = df[fname].astype(str)
            except Exception:
                df[fname] = ''
            continue

    # Final guard: if any tz-aware dtypes remain, drop tz or stringify
    tz_cols = [c for c in df.columns if ptypes.is_datetime64tz_dtype(df[c].dtype)]
    if tz_cols:
        for c in tz_cols:
            try:
                df[c] = df[c].dt.tz_convert('UTC').dt.tz_localize(None)
            except Exception:
                df[c] = df[c].astype(str)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    subject = "Direct Call & I Alert Call Status Auto Report"
    body = f"""
    <p>Dear Team,</p>

    <b>Please find below the Call status of Direct & I Alert  report of previous day and ensure completion of details not closed.:</b>

    {direct_call_table}
    <br><br>
    {ialert_call_table}
    <p>Regards,<br>Danlaw Service Team</p>
    """

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email="crscdanlaw@danlawtechnologies.com",
        to=["arung@danlawtech.com",
            "dilipkumarn@danlawtech.com",
            "eastdanlaw@danlawtech.com",
            "eliyasp@danlawtech.com",
            "gayadharm@danlawtech.com",
            "gowthamv@danlawtech.com",
            "swamyv@danlawtech.com",
            "kunal@danlawtech.com",
            "narendrareddyg@danlawtech.com",
            "rajendrans@danlawtech.com",
            "rishwanthr@danlawtech.com",
            "sales@danlawtech.com",
            "service@danlawtech.com",
            "sivanambirajant@danlawtech.com",
            "upendram@danlawtech.com",
            "yoganandam@danlawtech.com",
            "sales@danlawtech.com"
],
        cc=["sales@danlawtech.com","rajendrans@danlawtech.com"]
    )
    email.content_subtype = "html"
    # Attach Excel file
    email.attach(
        f"DirectCall_RawData_{today.strftime('%Y_%m')}.xlsx",
        excel_buffer.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    email.send()

send_direct_call_status_report = send_combined_status_report

if __name__ == '__main__':
    month_start = date.today().replace(day=1)
    qs = DirectCall.objects.filter(
        call_type='Direct Call',
        date_of_complaint__date__gte=month_start
    ).exclude(call_status__isnull=True).exclude(call_status__exact='').values_list('call_status', flat=True).distinct()
    print(qs.query)
    print(list(qs))
