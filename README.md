# Norway power market platform

A small data project about hourly electricity prices in Norway, built on Azure. I add to it step by step and write down what I have done.

## Status

- [x] Day 1: Azure storage basics and first sample of real price data
- [x] Day 2: Budget alert, Python script for all five price areas, daily run with GitHub Actions
- [ ] Store the raw files in Azure Data Lake Storage
- [ ] Automated tests
- [ ] Add consumption and weather data
- [ ] Bronze, silver and gold layers in Databricks
- [ ] Price forecast compared with a simple baseline
- [ ] Unusual price days explained with SHAP
- [ ] Power BI dashboard through Microsoft Fabric


## Done so far

### Day 1 (5 October 2026)

I created a resource group, put a storage account in it, and made a container for my files. Then I uploaded one day of price data for the Oslo area (NO1).

The part I liked most: I tried to open the file with only its URL, and Azure refused, because public access is turned off by default. Then I created a SAS token, which is a temporary, read-only key, and the same file opened. Seeing it fail first made the security model much easier to understand.

At the end I deleted the whole resource group, so nothing keeps running and costing money.

### Day 2 (6 October 2026)

I set a budget alert in Azure first, so I get an email if I ever spend more than a few dollars. Then I created the resource group that will hold the project.

After that I moved to Python. I explored the price API in a notebook and checked that each day has 24 hourly rows, with no empty or duplicate values. Then I turned the code into a small script, `fetch_prices.py`. It fetches all five price areas (NO1 to NO5) for one day and saves the raw files without changing them. If the data is missing or the row count looks wrong, it stops with an error instead of saving something broken.

One thing surprised me: on this day the average price in the south (NO2) was about 16 times higher than in the north (NO4).

The last step was a GitHub Actions workflow that runs the script every morning and commits the new files. From now on the data collects itself.

## Data sources

- Electricity prices: Strømpriser levert av [Hva koster strømmen.no](https://www.hvakosterstrommen.no). They get the prices from ENTSO-E. Prices are without VAT.
