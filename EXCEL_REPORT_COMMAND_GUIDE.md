# AIS140 Excel Report Generation - Command Usage Guide

## Installation

First, install the required Excel library:

```bash
pip install openpyxl
```

## Generate Excel Reports

### Generate Comprehensive Report (Excel with 2 sheets)
```bash
python manage.py generate_ais140_reports --report-type=comprehensive --format=excel
```

### Generate D1 Remarks Report (Excel)
```bash
python manage.py generate_ais140_reports --report-type=d1_remarks --format=excel
```

### Generate Both Reports (Excel)
```bash
python manage.py generate_ais140_reports --report-type=all --format=excel
```

### Custom Output Directory
```bash
python manage.py generate_ais140_reports --report-type=all --format=excel --output-dir=/path/to/reports/
```

## Excel File Structure

### Comprehensive Report (`AIS140_Report_YYYYMMDD_HHMMSS.xlsx`)

**Sheet 1: Report**
- Column 1: State
- Columns 2-16: Metrics
  - New Requests (yesterday)
  - Old Pending
  - Total
  - Cancelled
  - Temp Cert Done
  - SIM Exp (Expired)
  - SIM Act Pending
  - Top Up Reqd
  - Wrong Mapping
  - Fuse to Check
  - SOS/Wiring
  - Body Building
  - D2 Temp Cert
  - Danlaw Resp
  - Cust Supp

Features:
- ✅ Professional styling with header colors
- ✅ Grand Total row (yellow background)
- ✅ Frozen header row for easy scrolling
- ✅ Auto-sized columns
- ✅ Borders and alignment

**Sheet 2: Data**
- All AIS140 records with key fields:
  - Unique ID
  - Date of Request
  - State
  - Chassis No, Engine No, PSN No
  - Vehicle details
  - Customer information
  - RTO/Dealer info
  - Request status
  - D1/D2 remarks
  - Completion info
  - SIM status

Features:
- ✅ All raw data exported
- ✅ Professional formatting
- ✅ Frozen header row
- ✅ Bordered cells
- ✅ Ordered by date (newest first)

## CSV Format (Legacy)

If you prefer CSV format (without Excel):

```bash
python manage.py generate_ais140_reports --report-type=all --format=csv
```

## File Output Location

By default, files are saved to: `media/reports/`

Files are named with timestamp:
- `AIS140_Report_20250205_143022.xlsx`
- `d1_remarks_report_20250205_143022.csv`
- `comprehensive_report_20250205_143022.csv`

## Scheduled Generation

### Using Linux Cron (Daily 8 AM)
```bash
0 8 * * * cd /path/to/project && python manage.py generate_ais140_reports --report-type=all --format=excel
```

### Using Windows Task Scheduler
1. Create a batch file `generate_report.bat`:
```batch
@echo off
cd C:\path\to\project
python manage.py generate_ais140_reports --report-type=all --format=excel
```

2. Schedule via Task Scheduler with daily trigger

## Python Script (Programmatic Use)

```python
from django.core.management import call_command

# Generate comprehensive Excel report
call_command('generate_ais140_reports', 
    report_type='comprehensive', 
    format='excel',
    output_dir='media/reports/')

# Or in your code
import os
os.system('python manage.py generate_ais140_reports --report-type=all --format=excel')
```

## Troubleshooting

### ImportError: No module named 'openpyxl'
Solution: Install openpyxl
```bash
pip install openpyxl
```

### File permission denied
Solution: Ensure the output directory exists and is writable
```bash
mkdir -p media/reports
chmod 755 media/reports
```

### No data in report
Check if:
1. AIS140Request table has records
2. Records have `state` field populated
3. Date filters are correct (compares with yesterday)

### Excel file is corrupted
Try regenerating the report. If issue persists, use CSV format instead.

## Output Examples

### Report Sheet Preview
```
State              | New Requests | Old Pending | Total | Cancelled | ... | Cust Supp
ANDHRA PRADESH     | 11          | 0           | 11    | 1         | ... | 0
MAHARASHTRA        | 6           | 25          | 31    | 0         | ... | 4
...
Grand Total        | 89          | 293         | 375   | 1         | ... | 58
```

### Data Sheet Preview
```
Unique ID       | Date of Request      | State           | Chassis No | Engine No | ...
DTILAIS-250110  | 2025-02-04 10:30:00 | MAHARASHTRA     | MH123K    | ENG001   | ...
DTILAIS-250109  | 2025-02-03 14:15:00 | TAMIL NADU      | TN456L    | ENG002   | ...
```

## Command Examples

Generate both reports in Excel daily:
```bash
python manage.py generate_ais140_reports --report-type=all --format=excel --output-dir=media/reports/
```

Generate only comprehensive report with custom location:
```bash
python manage.py generate_ais140_reports --report-type=comprehensive --format=excel --output-dir=/backups/ais140/
```

View help:
```bash
python manage.py generate_ais140_reports --help
```
