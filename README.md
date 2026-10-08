# Norway power market platform

A small data project about hourly electricity prices in Norway, built on Azure. I add to it step by step and write down what I have done.

## Status

- [x] Day 1: Azure storage basics and first sample of real price data
- [x] Day 2: Budget alert, Python script for all five price areas, daily run with GitHub Actions
- [x] Day 3: Raw files stored in Azure Data Lake Storage, uploaded by the daily run
- [x] Day 3: Data-quality tests in GitHub Actions, on every push and in the daily run
- [x] Day 4: Hourly consumption data from Elhub, with its own data-quality tests
- [ ] Add weather data
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

### Day 3 (7 October 2026)

I started by checking yesterday's daily run. It had not started on its own this morning. The workflow file was fine; GitHub just does not promise an exact time for scheduled runs. So I started it by hand and added a second run time later in the day as a backup. Running twice is safe, because the job only commits when something has changed.

Then I gave the raw data a home in Azure. I created a storage account with hierarchical namespace turned on, which makes it Azure Data Lake Storage Gen2: it has real folders instead of one flat list of files. Inside it I made a container called `raw`.

The daily run needs permission to put files there. I created a SAS token for that one container that can only create and write files, not read or delete them, and it expires after a month. The token is stored in GitHub Secrets, so it never appears in the code.

The new script, `upload_to_azure.py`, copies every raw file into a folder for its day, for example `raw/prices/2026-10-07/`. The workflow now fetches the prices, commits them here, and then uploads them to the data lake. After the first run I opened the container in the portal and found all 15 files in their folders, five for each day.

Last, I wrote my first automated tests. They open every raw file and check the row count, the required fields, and that no hour appears twice. GitHub Actions runs them on every push, and the daily run also runs them before it uploads anything to Azure. To be sure the tests really work, I broke one on purpose: the run turned red, GitHub emailed me, and the error named the exact file. Then I fixed it.

### Day 4 (8 October 2026)

Good news first: the daily run did start on its own yesterday after all. Both scheduled runs came, only about seven hours later than the time I set. For this data that is fine, because the prices for a day are published the day before.

Today I added a second data source: hourly electricity consumption from Elhub. I explored the API in a new notebook first. One request returns all five price areas, and every hour is split into five consumer groups, so a normal day has 120 rows per area.

The biggest difference from prices is timing. Prices are known a day ahead, but consumption is measured afterwards. On 8 October the newest complete day in the API was 6 October. So the new script, `fetch_consumption.py`, asks for the day two days back, checks the row count for every area, and skips the day if the file is already there.

I wrote four tests for the consumption files, with the same idea as the price tests: row count, required fields and no duplicate hours. All eight tests pass on the real files.

Finally I added the consumption step to the daily run and changed the upload script so that consumption files get their own folder in the data lake. If the consumption API is down one day, the run still commits the prices it already fetched, and then fails so that I get an email. I have not seen a scheduled run with these changes yet, so that is the first thing I will check tomorrow.

## Data sources

- Electricity prices: Strømpriser levert av [Hva koster strømmen.no](https://www.hvakosterstrommen.no). They get the prices from ENTSO-E. Prices are without VAT.
- Electricity consumption: [Elhub](https://api.elhub.no), open Energy Data API. Hourly consumption per price area and consumer group.
