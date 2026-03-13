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

### Step 6: Save to CSV

Save collected data to CSV with exact columns:

```csv
Address,Suburb,Price,Bedrooms,Bathrooms,Cars,Land Size,URL,include_swimming_pool,sale_method,listing_date,auction_date,description
455 Springvale Road,Glen Waverley,$1,950,000,4,2,2,756 sqm,https://...,No,Auction,10 Mar 2026,22 Mar 2026,Excellent family home in quiet street...
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

### Step 7: Export to Google Sheets

```bash
# Create Google Sheet and upload CSV
gcloud auth list  # Ensure authenticated
gsheet create "property_candidate_list_$(date +%Y%m%d_%H%M)" --title "Property Candidates"
gsheet upload /path/to/properties.csv --title "Property Candidates"
```

Or use Google Drive API:
```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Build drive service
service = build('drive', 'v3', credentials=creds)

# Create spreadsheet
file_metadata = {
    'name': f'property_candidate_list_{datetime.now().strftime("%Y%m%d_%H%M")}',
    'mimeType': 'application/vnd.google-apps.spreadsheet'
}
file = service.files().create(body=file_metadata, fields='id').execute()

# Upload CSV
media = MediaFileUpload('properties.csv', mimetype='text/csv')
service.files().update(fileId=file['id'], media_body=media).execute()
```

### Step 8: Share Sheet Link

Provide user with the Google Sheets URL for review.

## CSV Format Reference

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

## Tips

- Check multiple pages (realestate.com.au shows ~20 per page)
- Suburb spelling must match exactly for filtering
- Some prices shown as "Price on Request" - record as-is
- Look for pool in listing photos (swimming pool icon or visible pool)
- Export timestamp in filename for version tracking
