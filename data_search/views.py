from django.shortcuts import render, redirect
from .forms import DataRecordForm
from .models import DataRecord
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import requests
import json
from datetime import datetime, timedelta
def add_data_record(request):
    if request.method == 'POST':
        vin = request.POST.get('vin', '').strip()
        if vin:
            DataRecord.objects.create(vin=vin)
            return redirect(f'/data_search/search/?vin={vin}')  # Redirect to search with VIN
        else:
            error = "error."
            return render(request, 'data_search/add_data_record.html', {'vin': vin, 'error': error})
    return render(request, 'data_search/add_data_record.html')

def search_data(request):
    vin = request.GET.get('vin', '').strip()
    result = None
    if vin:
        result = DataRecord.objects.filter(vin__iexact=vin).first()
        if not result:
            result = DataRecord(vin=vin)
            result.save()
            print("Saved VIN:", vin)
    return render(request, 'data_search/add_data_record.html', {'result': result, 'vin': vin})
@require_GET
def fetch_external_data(request):
    vin = request.GET.get('vin', '').strip().upper()
    print("VIN received in backend:", vin)
    if not vin:
        return JsonResponse({'error': 'VIN required'}, status=400)

    api_url_1 = "https://api.al.drivewithdarby.com/v1/assets/dynamic/search"
    headers_1 = {
        "Authorization": "Bearer eyJhbGciOiJIUzM4NCJ9.eyJpc3MiOiJkYXJieSIsImp0aSI6ImJkNzVmYWIzLWNhNDktNDBiMi1iZGJjLThiYzJiMDllOTFlNyIsImlhdCI6MTc1MDg0NDc2OSwiZXhwIjoxNzgyMzgwNzY5LCJDSSI6NDIsIlVJIjoiMzFhZmUzMjgtZTIzYS00MDI2LWJkMGEtYmJkMzViMGRkODg0IiwiRU0iOiJWaXNod2FuYXRoLkdAYXNob2tsZXlsYW5kLmNvbSIsIlJJIjoiMWQ5MDllZTUtOWQ1ZS00Y2E3LWJjZmEtMzQ5YWUzM2YzMjIzIiwiVFkiOiJBRE1JTl9VU0VSIiwiRk4iOiJWaXNod2FuYXRoIiwiTE4iOiJHOiBEYW5sYXcgQXNzZXQgRHluYW1pYyBTZWFyY2giLCJQSSI6IjMxYWZlMzI4LWUyM2EtNDAyNi1iZDBhLWJiZDM1YjBkZDg4NCIsIlBOIjoiRGFubGF3IEFzc2V0IER5bmFtaWMgU2VhcmNoIiwiQUkiOiJjOWQ1YjViOS1lNjE4LTQ5OTktYmY1Mi1hNjQ4NTgwYjU0N2EiLCJBVCI6WyJBU1NFVDpSRUFEIiwiUkVQT1JUOlJFQUQiLCJMSVZFOlJFQUQiLCJDQU1QQUlHTjpSRUFEIiwiREFTSEJPQVJEOlJFQUQiXX0.LPPA6mVuKOH1L_KOvoe0r1anfuSMSjbuWyYdK7LVH82UGLKpQpsASMoSEHz81p0L",
        "Content-Type": "application/json"
    }
    payload_1 = {
        "assetType": "DEVICE",
        "filters": {"vin": [vin]}
    }
    resp1 = requests.post(api_url_1, headers=headers_1, json=payload_1, timeout=10)
    resp1.raise_for_status()
    assets = resp1.json().get("results", [])
    asset = next((a for a in assets if a.get("vin", "").strip().upper() == vin), None)
    if not asset:
        return JsonResponse({"error": f"No asset found with VIN: {vin}"}, status=404)
    asset_id = asset.get("assetId", "")

    # helper to convert milliseconds -> formatted string
    def ms_to_iso(ms):
        if not ms:
            return ""
        try:
            return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""

    # parse state & country from address (fallbacks)
    address = (asset.get("address") or "").strip()
    state = ""
    country = ""
    if address:
        parts = [p.strip() for p in address.split(",") if p.strip()]
        if len(parts) >= 2:
            state = parts[-2]
        if len(parts) >= 1:
            country = parts[-1]

    # Set date range for last 7 days
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=6)
    startTime = start_dt.strftime('%Y-%m-%dT00:00:00Z')
    endTime = end_dt.strftime('%Y-%m-%dT23:59:59Z')

    # Use new analytics-daily-summary API
    api_url_2 = (
        f"https://web.al.drivewithdarby.com/v1/messages/asset/{asset_id}/analytics-daily-summary"
        f"?startTime={startTime}&endTime={endTime}"
    )
    resp2 = requests.get(api_url_2, headers=headers_1, timeout=10)
    resp2.raise_for_status()
    analytics_data = resp2.json()

    # Build summary_table from new API structure
    summary_table = []
    for row in analytics_data.get("results", []):
        min_odo = row.get("min_odo", 0) or 0
        max_odo = row.get("max_odo", 0) or 0
        kms = max_odo - min_odo if max_odo and min_odo else 0
        summary_table.append({
            "date": datetime.strptime(row.get("date", ""), "%Y-%m-%d").strftime("%d-%m-%Y") if row.get("date") else "",
            "v_packets": row.get("v_count", 0) or 0,
            "a_packets": row.get("a_count", 0) or 0,
            "total_packets": (row.get("v_count", 0) or 0) + (row.get("a_count", 0) or 0),
            "start_odo": min_odo,
            "end_odo": max_odo,
            "kms": kms,
            "lat_0_5": row.get("cnt_0_5m", 0) or 0,
            "lat_5_15": row.get("cnt_5_15m", 0) or 0,
            "lat_15_30": row.get("cnt_15_30m", 0) or 0,
            "lat_30_1h": row.get("cnt_30_60m", 0) or 0,
            "lat_1h_3h": row.get("cnt_1_3h", 0) or 0,
            "lat_3h_6h": row.get("cnt_3_6h", 0) or 0,
            "lat_6h_12h": row.get("cnt_6_12h", 0) or 0,
            "lat_12_24h": row.get("cnt_12_24h", 0) or 0,
            "lat_gt_24h": row.get("cnt_gt_24h", 0) or 0,
        })

    # Add summary_row (total for all days)
    if summary_table:
        total_v_packets = sum(row["v_packets"] for row in summary_table)
        total_a_packets = sum(row["a_packets"] for row in summary_table)
        total_packets = sum(row["total_packets"] for row in summary_table)
        total_start_odo = summary_table[0]["start_odo"]
        total_end_odo = summary_table[-1]["end_odo"]
        total_kms = total_end_odo - total_start_odo
        total_lat_0_5 = sum(row["lat_0_5"] for row in summary_table)
        total_lat_5_15 = sum(row["lat_5_15"] for row in summary_table)
        total_lat_15_30 = sum(row["lat_15_30"] for row in summary_table)
        total_lat_30_1h = sum(row["lat_30_1h"] for row in summary_table)
        total_lat_1h_3h = sum(row["lat_1h_3h"] for row in summary_table)
        total_lat_3h_6h = sum(row["lat_3h_6h"] for row in summary_table)
        total_lat_6h_12h = sum(row["lat_6h_12h"] for row in summary_table)
        total_lat_12_24h = sum(row["lat_12_24h"] for row in summary_table)
        total_lat_gt_24h = sum(row["lat_gt_24h"] for row in summary_table)

        summary_row = {
            "date": "Summary",
            "start_odo": total_start_odo,
            "end_odo": total_end_odo,
            "kms": total_kms,
            "total_packets": total_packets,
            "a_packets": total_a_packets,
            "v_packets": total_v_packets,
            "lat_0_5": total_lat_0_5,
            "lat_5_15": total_lat_5_15,
            "lat_15_30": total_lat_15_30,
            "lat_30_1h": total_lat_30_1h,
            "lat_1h_3h": total_lat_1h_3h,
            "lat_3h_6h": total_lat_3h_6h,
            "lat_6h_12h": total_lat_6h_12h,
            "lat_12_24h": total_lat_12_24h,
            "lat_gt_24h": total_lat_gt_24h,
        }
    else:
        summary_row = None

    return JsonResponse({
        "summary_table": summary_table,
        "raw_data": analytics_data,
        "vin_details": {
            "vin": asset.get("vin", ""),
            "productSerialNumber": asset.get("productSerialNumber", "") or asset.get("assetName", ""),
            "productCode": asset.get("productCode", ""),
            "cardState": asset.get("cardState", ""),
            "cardStatus": asset.get("cardStatus", ""),
            "alertPacketKafkaPublishedTime": ms_to_iso(asset.get("kafkaAlertPacketPublishedTime")),
            "vpacketKafkaPublishedTime": ms_to_iso(asset.get("kafkaVPacketPublishedTime") or asset.get("kafkaVPacketPublishedTime")),
            "apacketKafkaPublishedTime": ms_to_iso(asset.get("kafkaAPacketPublishedTime") or asset.get("kafkaAPacketPublishedTime")),
            "firstCommunication": ms_to_iso(asset.get("firstCommunication")),
            "lastCommunication": ms_to_iso(asset.get("lastCommunication")),
            "comStatus": asset.get("comStatus", ""),
            "address": address,
            "state": state,
            "country": country,
        },
        "api_1_data": {
            "imei": asset.get("imei", "") or asset.get("imeiNumber", ""),
            "ignitionStatus": asset.get("ignitionStatus", ""),
            "vehicleBatteryPotential": asset.get("vehicleBatteryPotential", "") or asset.get("internalBatteryPotential", ""),
            "address": address,
            "comStatus": asset.get("comStatus", ""),
            "latestCsRenewalEndDate": ms_to_iso(asset.get("latestActivityEndDate") or asset.get("commercialExpiryDate") or asset.get("bootstrapExpiryDate")),
            "state": state,
            "country": country,
        },
        "summary_row": summary_row
    })
