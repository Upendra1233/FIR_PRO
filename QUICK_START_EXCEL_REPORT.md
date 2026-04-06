# Quick Start: Excel Report Generation

## 1️⃣ Install Required Package
```bash
pip install openpyxl
```

## 2️⃣ Choose Your Method

### Option A: Download from Web (Easiest)
1. Visit: `http://your-domain/ais140/reports/comprehensive/`
2. Click **"Download Excel Report"** button
3. Excel file downloads automatically

### Option B: Command Line (Automated)
```bash
python manage.py generate_ais140_reports --report-type=comprehensive --format=excel
```

## 3️⃣ Files Generated

Single Excel file with **2 sheets**:
- **Sheet 1 - "Report"**: State-wise metrics summary
- **Sheet 2 - "Data"**: All AIS140 records

## 📊 Excel File Contents

### Report Sheet
```
State              | New Req | Old Pend | Total | Cancelled | Temp Cert | SIM Exp | ... | Total Row
MAHARASHTRA        |   6    |    25    |  31   |     0     |     2     |    5    | ... |
TAMIL NADU         |  57    |   161    | 218   |     0     |    11     |    5    | ... |
...
Grand Total        |  89    |   293    | 375   |     1     |    99     |   111   | ... |
```

### Data Sheet
```
Unique ID    | Date         | State      | Chassis No | Engine | PSN | Vehicle | Customer | ...
DTILAIS-250110 | 2025-02-04 | MAHARASH... | MH123K     | ENG001 | ... | ...     | ...      | ...
DTILAIS-250109 | 2025-02-03 | TAMIL NAD.. | TN456L     | ENG002 | ... | ...     | ...      | ...
```

## 🚀 Common Commands

| Task | Command |
|------|---------|
| Download Excel from web | Visit `/ais140/reports/comprehensive/` and click button |
| Generate via command line | `python manage.py generate_ais140_reports --report-type=comprehensive --format=excel` |
| Generate all reports | `python manage.py generate_ais140_reports --report-type=all --format=excel` |
| Custom output folder | `python manage.py generate_ais140_reports --report-type=all --format=excel --output-dir=/path/` |

## 📍 Where Files Are Saved

Default: `media/reports/`

Example filename: `AIS140_Report_20250205_143022.xlsx`

## ⚙️ Schedule Daily Reports

**Linux/Mac** - Add to crontab:
```bash
0 8 * * * cd /path/to/project && python manage.py generate_ais140_reports --report-type=all --format=excel
```

**Windows** - Create batch file and use Task Scheduler

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError: openpyxl | Run `pip install openpyxl` |
| File permission denied | Create `media/reports/` folder |
| No data in report | Check AIS140Request has records with `state` field |
| Excel won't open | Try regenerating or use CSV format |

## 📋 Verification Checklist

- [ ] openpyxl installed (`pip install openpyxl`)
- [ ] Web report page accessible (`/ais140/reports/comprehensive/`)
- [ ] "Download Excel Report" button visible
- [ ] Excel file downloads when clicked
- [ ] File has 2 sheets: "Report" and "Data"
- [ ] Report sheet shows state metrics
- [ ] Data sheet shows all records
- [ ] Grand Total row is present and accurate
- [ ] Command line works: `python manage.py generate_ais140_reports --help`

## 🎉 You're Ready!

Your Excel report system is set up and ready to use. 

**Start using it now:**
- For quick download: Visit `/ais140/reports/comprehensive/`
- For automation: Set up scheduled command in cron or Task Scheduler

## 📖 Full Documentation

- `EXCEL_REPORT_IMPLEMENTATION.md` - Complete implementation details
- `EXCEL_REPORT_COMMAND_GUIDE.md` - Detailed command reference
- `AIS140_AUTO_REPORTS_GUIDE.md` - Overall system guide
