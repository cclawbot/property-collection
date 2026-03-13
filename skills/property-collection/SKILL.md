---
name: property-collection
description: Collect Melbourne property listings from realestate.com.au into CSV with Google Sheets export. Use when user wants to find properties in Melbourne suburbs, search with filters (price, beds, baths, land size), build candidate list for property investment, or enrich property data.
---

# Property Collection Skill

Workflow for collecting Melbourne property listings from realestate.com.au and building a candidate list.

## Pre-requisites

- OpenClaw browser tool available
- Google Sheets API access (via gcloud authenticated user)
- Property search filters defined

## Workflow

### Step 1: Define Search Criteria

Before starting, confirm with user:
- Target suburbs (e.g., Glen Waverley, Mount Waverley, Doncaster, etc.)
- Price range (e.g., $1.8M - $2.1M)
- Minimum bedrooms (e.g., 4)
- Minimum bathrooms (e.g., 2)
- Minimum land size (e.g., 500 sqm)

### Step 2: Spawn Browser & Search

```python
# Use browser tool to open realestate.com.au
browser(action="start", profile="openclaw")
browser(action="navigate", url="https://www.realestate.com.au/buy")
```

### Step 3: Apply Filters

In the browser:
1. Enter suburb name in location search
2. Apply price range filter
3. Apply bedroom filter (4+)
4. Apply bathroom filter (2+)
5. Apply land size filter (500+)
6. Set property type to "House"

### Step 4: Collect Property Data

For each listing on results page, record:
- Address
- Suburb
- Price
- Bedrooms
- Bathrooms
- Cars
- Land Size
- URL (listing link)
- **include_swimming_pool** (Yes/No/Unknown - check listing photos/description)
- **sale_method** (Auction/Private Sale/Unknown)
- **listing_date** (exact date listed, e.g., "12 Mar 2026")
- **auction_date** (exact auction date if applicable, e.g., "22 Mar 2026" or "TBC")
- **description** (property description/summary from listing, max 500 chars)

### Step 5: Navigate Pages

Click "Next" or pagination until no more results. Collect all properties across all pages for each suburb.

### Step 6: Validate Existing URLs (Incremental Run Only)

**For Incremental Runs, validate ALL existing properties BEFORE adding new ones:**

1. **Load existing CSV** with all properties

2. **For each existing property**:
   - Make HTTP GET request to the property URL
   - Check response:
     - **200 OK**: Property still active → keep in CSV
     - **404/410/Gone**: Property removed/sold → **REMOVE from CSV** (log as "REMOVED: URL invalid")
     - **302/Redirect**: May be sold → investigate manually, mark status as "Sold?"
   
3. **Batch efficiency**:
   ```python
   import concurrent.futures
   
   def check_url(row):
       try:
           r = requests.head(row['URL'], timeout=10, allow_redirects=True)
           if r.status_code in [200, 301, 302]:
               return row, "active"
           else:
               return row, "removed"
       except:
           return row, "error"
   
   # Check in parallel (max 10 concurrent)
   with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
       results = list(executor.map(check_url, existing_rows))
   ```

4. **Update CSV**: Remove invalid properties, keep active ones

**Note**: Skip this step for Initial Run (no existing CSV to validate).

### Step 7: Save to CSV (with Duplicate Check)

**This step supports both Initial Run and Incremental Run:**

1. **Check if CSV exists**:
   - If existing CSV found, load addresses into a set for deduplication
   - If no CSV exists, start fresh

2. **For each property collected**:
   - Normalize address (strip whitespace, handle variations)
   - Check if address already in existing CSV
   - **If duplicate found**: Skip (log as "SKIPPED: already exists")
   - **If new**: Append to CSV

3. **Save to CSV** with exact columns:

```csv
Address,Suburb,Price,Bedrooms,Bathrooms,Cars,Land Size,URL,include_swimming_pool,sale_method,listing_date,auction_date,description,status
455 Springvale Road,Glen Waverley,$1,950,000,4,2,2,756 sqm,https://...,No,Auction,10 Mar 2026,22 Mar 2026,Excellent family home...,Active
```

**Address Normalization for Duplicate Check**:
```python
import re

def normalize_address(addr):
    # Strip extra spaces, convert to lowercase
    addr = addr.strip().lower()
    # Remove unit numbers for comparison (e.g., "2A" vs "2")
    addr = re.sub(r'^[0-9]+[a-z]+\s', '', addr)  # "2A Springvale" -> "Springvale"
    # Remove common suffixes
    addr = re.sub(r'\s+(road|st|avenue|dr|drive|cr|crescent|ave|place)$', '', addr)
    return addr

# Usage
existing_addresses = set()
with open('properties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_addresses.add(normalize_address(row['Address']))

# Check before adding
if normalize_address(new_address) not in existing_addresses:
    writer.writerow(new_row)
```

**Column Definitions**:
- **Address**: Street address (e.g., "455 Springvale Road")
- **Suburb**: Suburb name (e.g., "Glen Waverley")
- **Price**: Listed price (e.g., "$1,950,000" or "Price on Request")
- **Bedrooms**: Number of bedrooms
- **Bathrooms**: Number of bathrooms
- **Cars**: Garage/carport spaces
- **Land Size**: Land area (e.g., "756 sqm")
- **URL**: Full URL to listing
- **include_swimming_pool**: Yes/No/TBC - Look for pool in listing photos or description
- **sale_method**: Auction/Private Sale/Unknown - Check listing for auction details
- **listing_date**: Exact date property was listed (e.g., "12 Mar 2026")
- **auction_date**: Exact auction date if applicable (e.g., "22 Mar 2026", "TBC", or empty)
- **description**: Property description/summary from listing (max 500 characters, strip HTML)

### Step 8: Export to Google Sheets

**Determine Run Mode**:

| Mode | When | Search Range | Action |
|------|------|--------------|--------|
| **Initial Run** | First time / fresh start | Past 30 days | Create NEW Google Sheet |
| **Incremental Run** | Subsequent updates | Past 10 days | Add to EXISTING Sheet |

**Initial Run** (first time):
```bash
# Search 30 days, create new sheet
gsheet create "property_candidate_list_$(date +%Y%m%d_%H%M)" --title "Property Candidates"
```

**Incremental Run** (update existing):
```python
# Add to existing sheet (by spreadsheet ID)
from googleapiclient.discovery import build
service = build('drive', 'v3', credentials=creds)

# Get existing sheet ID (store this after initial run)
EXISTING_SHEET_ID = "YOUR_SHEET_ID_HERE"

# Read CSV and append to sheet
# Use sheets API to append rows
```

### Step 9: Share Sheet Link

Provide user with the Google Sheets URL for review.

### Important Limitation: Removed/Sold Properties

**Problem**: Incremental runs cannot detect properties that have been:
- Sold
- Withdrawn from market
- Passed in at auction

**Solution** (Automated in Step 6.5):
1. **URL Check**: Before adding new listings, validate ALL existing property URLs
2. **Auto-Remove**: If URL returns 404/410, automatically remove from CSV
3. **Monthly Full Check**: Still recommend monthly full 30-day re-run for edge cases

### Step 7: Export to Google Sheets

Exact column order for compatibility:

```
Address,Suburb,Price,Bedrooms,Bathrooms,Cars,Land Size,URL,include_swimming_pool,sale_method,listing_date,auction_date,description
```

- **Address**: Street address (e.g., "455 Springvale Road")
- **Suburb**: Suburb name (e.g., "Glen Waverley")
- **Price**: Listed price (e.g., "$1,950,000" or "Price on Request")
- **Bedrooms**: Number of bedrooms
- **Bathrooms**: Number of bathrooms
- **Cars**: Garage/carport spaces
- **Land Size**: Land area (e.g., "756 sqm")
- **URL**: Full URL to listing
- **include_swimming_pool**: Yes/No/TBC
- **sale_method**: Auction/Private Sale/Unknown
- **listing_date**: Date listed (e.g., "12 Mar 2026")
- **auction_date**: Auction date if known (e.g., "22 Mar 2026", "TBC", or empty)
- **description**: Property description summary (max 500 chars)
- **status**: Active/Sold/Withdrawn (default: Active, manual update needed)

## Tips

### Running Modes

**Initial Run** (first time):
- Start with empty CSV or delete existing file
- Search past 30 days
- All properties will be collected
- Skip Step 6 (no existing CSV to validate)

**Incremental Run** (update existing):
1. **Step 6 FIRST**: Validate existing URLs, remove invalid ones
2. **Then Step 7**: Search past 10 days, add new properties (skip duplicates)
3. Keep existing CSV file

### General Tips

- Check multiple pages (realestate.com.au shows ~20 per page)
- Suburb spelling must match exactly for filtering
- Some prices shown as "Price on Request" - record as-is
- Look for pool in listing photos (swimming pool icon or visible pool)
- Export timestamp in filename for version tracking
