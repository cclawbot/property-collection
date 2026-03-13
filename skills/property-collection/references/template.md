# CSV Template

```csv
Address,Suburb,Price,Bedrooms,Bathrooms,Cars,Land Size,URL,include_swimming_pool,sale_method,listing_date,auction_date,description
455 Springvale Road,Glen Waverley,$1,950,000,4,2,2,756 sqm,https://www.realestate.com.au/property-455-springvale-road-glen-waverley-vic-3150,No,Auction,10 Mar 2026,22 Mar 2026,Excellent family home in quiet street close to schools and shops...
28 Angus Drive,Glen Waverley,$1,880,000,4,2,2,650 sqm,https://www.realestate.com.au/property-28-angus-drive-glen-waverley-vic-3150,TBC,Private Sale,08 Mar 2026,,Spacious modern family home with open plan living...
2A Gwingana Crescent,Glen Waverley,$2,050,000,5,3,2,612 sqm,https://www.realestate.com.au/property-2a-gwingana-crescent-glen-waverley-vic-3150,Yes,Auction,05 Mar 2026,29 Mar 2026,Stunning family residence with pool and landscaped gardens...
```

# Column Definitions

| Column | Values | Where to Find |
|--------|--------|---------------|
| Address | Full street address | Listing header |
| Suburb | Suburb name | Listing header |
| Price | $X,XXX,XXX or "Price on Request" | Listing price section |
| Bedrooms | Number (1-10+) | Property features |
| Bathrooms | Number (1-10+) | Property features |
| Cars | Number | Property features |
| Land Size | "XXX sqm" or "XXX sqm (XXX ac)" | Land details |
| URL | Full listing URL | Browser address bar |
| include_swimming_pool | Yes/No/TBC | Photos + description |
| sale_method | Auction/Private Sale/Unknown | Listing details section |
| listing_date | "DD MMM YYYY" | Listing metadata |
| auction_date | "DD MMM YYYY" or "TBC" or empty | Auction details |
| description | Max 500 chars | Listing description text |

# Sample Suburbs (Melbourne)

## Eastern Suburbs (Popular)
- Glen Waverley
- Mount Waverley
- Doncaster
- Doncaster East
- Balwyn
- Balwyn North
- Camberwell
- Kew
- Kew East
- Hawthorn
- Glen Iris
- Surrey Hills
- Blackburn
- Box Hill
- Templestowe
- Templestowe Lower

## Southern Suburbs
- Wheelers Hill
- Wantirna South
- Ashwood
- Chadstone
- Oakleigh
- Clayton
- Ashburton

## Other Areas
- Ivanhoe
- Bentleigh
- Malvern East
- Canterbury
- Mont Albert
- Vermont

# Filter Reference

## realestate.com.au URL Pattern

```
https://www.realestate.com.au/buy?suburb={SUBURB}&minPrice={MIN_PRICE}&maxPrice={MAX_PRICE}&bedrooms={MIN_BEDS}&bathrooms={MIN_BATHS}&land={MIN_LAND}&propertyType=house
```

Example:
```
https://www.realestate.com.au/buy?suburb=glen-waverley-3150&minPrice=1800000&maxPrice=2100000&bedrooms=4&bathrooms=2&land=500&propertyType=house
```

# Data Collection Tips

## Swimming Pool Detection
Look for:
- Pool in photos
- "swimming pool" icon in features
- Description mentions "pool", "swimming pool"

## Sale Method
- "Auction" - clearly stated
- "Private Sale" or "For Sale" or price shown
- "Unknown" - can't determine

## Listing Date
- Usually shown as "Listed [date]" or "Listed X days ago"
- Convert "3 days ago" to actual date

## Auction Date
- Shown in auction section
- May say "Auction" with date
- May say "TBC" or "To be advised"
- Leave empty if no auction

## Description
- Copy from listing description
- Strip HTML tags
- Truncate to 500 characters max
- Include key selling points
