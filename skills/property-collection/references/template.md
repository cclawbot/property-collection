# CSV Template

```csv
Address,Suburb,Price,Bedrooms,Bathrooms,Cars,Land Size,URL,include_swimming_pool
455 Springvale Road,Glen Waverley,$1,950,000,4,2,2,756 sqm,https://www.realestate.com.au/property-455-springvale-road-glen-waverley-vic-3150,No
28 Angus Drive,Glen Waverley,$1,880,000,4,2,2,650 sqm,https://www.realestate.com.au/property-28-angus-drive-glen-waverley-vic-3150,TBC
2A Gwingana Crescent,Glen Waverley,$2,050,000,5,3,2,612 sqm,https://www.realestate.com.au/property-2a-gwingana-crescent-glen-waverley-vic-3150,Yes
```

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

# Swimming Pool Detection

## What to look for:
1. **Photos**: Look for pool in listing images
2. **Icons**: Swimming pool icon in property features
3. **Description**: Text mentions "pool", "swimming pool", "pool area"
4. **Floor plan**: May show pool location

## Values:
- **Yes**: Pool confirmed visible in photos or description
- **No**: Explicitly stated no pool, or clear from photos
- **TBC**: Unable to determine from listing
