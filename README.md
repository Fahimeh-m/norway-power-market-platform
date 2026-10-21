# Norway power market platform

A small data project about hourly electricity prices in Norway, built on Azure. I add to it step by step and write down what I have done.

## Status

- [x] Day 1: Azure storage basics and first sample of real price data
- [x] Day 2: Budget alert, Python script for all five price areas, daily run with GitHub Actions
- [x] Day 3: Raw files stored in Azure Data Lake Storage, uploaded by the daily run
- [x] Day 3: Data-quality tests in GitHub Actions, on every push and in the daily run
- [x] Day 4: Hourly consumption data from Elhub, with its own data-quality tests
- [x] Day 5: Weather forecast for all five price areas, fetched and stored by the daily run
- [x] Day 6: Data-quality tests for the weather files
- [x] Day 7: Missed consumption days fetched automatically, and sign-in to Azure without stored secrets (OIDC)
- [x] Day 8: Databricks reads the raw files from Azure, with read-only access
- [x] Day 9: First bronze table in Databricks, for prices
- [x] Day 10: Five full days without help (14 to 18 October), bronze tables for consumption and weather, silver prices in UTC
- [x] Day 11: Silver tables for consumption and weather, a first gold table, and the error of a simple baseline
- [x] Day 12: Seven full days without help, and a star schema in Power BI Desktop with tables for price area and date
- [ ] Power BI report: DAX measures for prices, consumption and the baseline error, and a first report page
- [ ] Keep Databricks fed with new data after the Azure free credit ends
- [ ] Work on this repository from my own computer with Git: clone, branches and pull requests
- [ ] Security scans in GitHub Actions: Bandit for the code, pip-audit for the packages
- [ ] Price forecast compared with a simple baseline
- [ ] Unusual price days explained with SHAP
- [ ] Later: publish the report through Microsoft Fabric

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

Finally I added the consumption step to the daily run and changed the upload script so that consumption files get their own folder in the data lake. If the consumption API is down one day, the run still commits the prices it already fetched, and then fails so that I get an email. In the afternoon the scheduled run came on its own with these changes: it fetched the prices for the day, passed all eight tests and uploaded 22 files. I opened the container in the portal and found the new `consumption` folder next to `prices`. It was also the first day the prices arrived without me pressing anything.

### Day 5 (9 October 2026)

The daily run came on its own for the second day, again in the afternoon. This was the first time it fetched consumption by itself: the log said it saved the file for 7 October, two days back, as planned. I found the new folder in the data lake too.

Then I tried to break the consumption script by asking for tomorrow. Elhub answered with zero rows, the script stopped with an error and saved nothing. That is what I want: a bad answer should never reach the raw folder.

The third data source is weather. I use the Locationforecast API from MET Norway. It needs no key, but every request must say who is asking, so the script sends the project name and my GitHub page in the User-Agent header. I picked one city for each price area: Oslo, Kristiansand, Trondheim, Tromsø and Bergen. The API gives the forecast for the next nine days, and only the current one, so a forecast I do not save today is gone tomorrow. The number of time steps is not fixed (I saw 85 and 86 on the same evening), so `fetch_weather.py` checks for at least 48 instead of an exact number. All times are in UTC.

Last, I added the weather step to the daily run and one line to the upload script. The weather step runs even if an earlier step fails, because this data cannot be fetched later. I started the run by hand once to check: it saved five forecast files and they arrived in a new `weather` folder in the data lake. Tests for the weather files are next.

### Day 6 (10 October 2026)

Today started with an email from GitHub: the scheduled run had failed. The run came earlier than on the other days, and Elhub had no rows yet for 8 October, so the consumption script stopped with the same error I caused on purpose yesterday. The good part is what happened next. The weather step still ran and saved five forecast files, and the prices and forecasts were committed here. The tests and the upload were skipped, so today's files are in this repository but not yet in the data lake. The second run of the day will try again.

Then I wrote four tests for the weather files, in `tests/test_weather_files.py`: there is at least one file, every file has at least 48 time steps, every time step has a time, an air temperature and a wind speed, and no time appears twice. With the price and consumption tests that makes 12, and all of them pass.

To check that the new tests can really fail, I made one too strict on purpose: exactly 85 time steps instead of at least 48. The run turned red and named yesterday's Oslo file, which has 86. Nothing was wrong with the file; my rule was wrong. A test that is too strict fails on healthy data, so I changed it back and the run turned green again.

### Day 7 (13 October 2026)

I came back after two days away and found four failed runs in a row, two on Saturday and two on Sunday. Each time Elhub had no rows yet for the day two days back, so consumption for 8 and 9 October was never saved. Prices and weather forecasts were still fetched every day, because those steps run anyway, and they reached the data lake on Monday when the runs turned green again.

The real problem was in my script: it only ever asked for one day, so a day that came late was lost. I changed `fetch_consumption.py` to look at the last seven days and fetch every day that has no file yet. If Elhub has nothing for a day, the script says so and moves on instead of failing. It still fails if a day is missing after a week, or if only some price areas have data. I started the run by hand, and it saved 8, 9 and 11 October.

Then I removed the last secret from the daily run. Until now the upload used a SAS token stored in GitHub Secrets. Now GitHub Actions signs in to Azure with OpenID Connect. I registered an app in Microsoft Entra ID, added a federated credential that trusts only this repository and its main branch, and gave the app the Storage Blob Data Contributor role on the `raw` container only. On every run GitHub gets a short-lived token, so no password or key is stored anywhere. To be sure the new sign-in was really used, I checked the upload time of today's files in the portal.

Last, I deleted the SAS token from GitHub and rotated the storage key it was signed with, so the old token no longer works. I ran the workflow once more and it was green, so nothing depends on the old token any more.

### Day 8 (15 October 2026)

I signed up for Databricks Free Edition and tested two things first. The price API answered 200, so Databricks can reach the internet. My storage account answered 409 (public access not permitted), so the road to Azure was open but the door was locked, as it should be.

I created a second app registration in Microsoft Entra ID, only for Databricks, and gave it the Storage Blob Data Reader role on the raw container. The daily workflow can write; Databricks can only read. I made a client secret that expires in 90 days and put it straight into the Databricks secret store, so the notebook only contains IDs.

From a notebook I listed the price files for 14 October: five files, one per price area. Then I tried to upload a test file from Databricks, and Azure refused it. That was the result I wanted.

I didn't use Azure Key Vault. Databricks Free Edition runs outside my Azure subscription and has its own secret store, so Key Vault would only add one more secret to manage.

### Day 9 (16 October 2026)

The daily run has now been green on its own for two full days, 14 and 15 October, with both runs each day.

Today I built my first bronze table in Databricks. The notebook signs in to Azure with yesterday's read-only app, lists the price files and downloads them. My first count was 72 instead of 60. Because the storage account is a data lake with real folders, the list also returned the 12 day folders. I kept only the names that end with `.json` and got 60 files: five price areas for 12 days.

I didn't change the data. I only added three columns to every row: the price area (taken from the file name), the source file, and the time I loaded it. With the source file, any strange value can be traced back to its file in Azure. The table `bronze_prices` has 1,440 rows, 24 hours for each of the 60 files.

Then I broke it on purpose. I wrote the table again with append instead of overwrite, and it had 2,880 rows: every hour twice. Writing it with overwrite brought it back to 1,440, so running the notebook again does not create duplicates.

I also noticed that the price times are in Norwegian time (+02:00), while the weather forecasts are in UTC. In the silver layer I will turn all times into UTC, so the same hour lines up across sources. The two Databricks notebooks are now in the `databricks` folder.

### Day 10 (19 October 2026)

After a weekend away I checked the Actions tab. Every scheduled run from 14 to 18 October was green, two runs each day. In that time I didn't touch the workflow, the scripts or the secrets. That is five full days in a row without any help from me, and it closes the first part of the project: collecting the data every day.

Then I built bronze tables for consumption and weather. A consumption file holds one day for all five price areas in nested JSON, so I looped through each area and each row: 13 files and 7,800 rows. The price area is already in every row, so I only added the source file and the load time. The consumption times are in Norwegian time too, like the prices.

The weather files were harder. The first forecast steps have precipitation, but steps several days ahead only have temperature, wind and similar values. So in bronze I kept each step's data as a JSON string, unchanged, and I will open it in the silver layer. The table has 4,709 rows from 55 files. The same hour appears in several files, because every day's forecast looks about ten days ahead; the source file column tells them apart.

Last, I started the silver layer with prices. I turned the Norwegian times into UTC with code, kept only the columns I need with clearer names, and removed duplicate hours. The first row from the 5 October file is now 4 October at 22:00 UTC. That is why I didn't just subtract two hours by hand: the date can change, and Norway changes its clock on 25 October. The silver table reads from the bronze table inside Databricks, not from Azure.

### Day 11 (20 October 2026)

The daily run was green on 19 October too, so it has now run six full days without help.

I started with the silver table for consumption. Like prices, the times became UTC. This time I removed duplicates on three columns, price area, consumer group and hour, because every area has five rows for each hour. The `last_updated_utc` column shows the delay I built the seven-day check for: the data for 5 October was published by Elhub on 7 October.

The weather silver table was the interesting one. I opened the JSON string from bronze and took three values: air temperature, wind speed and precipitation for the next hour. Steps far ahead have no precipitation, so that value is empty there, not zero. Then I counted: 4,709 rows but only 1,600 different area and hour pairs. Every hour is forecast several times, once in each daily file. For example, Bergen at 12:00 UTC on 22 October was forecast in nine files, from 12 to 20 October, and the temperature moved between 10.5 and 12.5 degrees. I kept every forecast and added the date it was made, taken from the file name. The choice of which forecast to use comes later.

Before the gold layer I checked the first and last hour in each table, and found that prices stopped on 16 October. The layers don't update themselves: the bronze table only knew the files from the day I built it. I ran all the notebooks again in order, bronze first and then silver. Now prices go to 20 October (1,920 rows), consumption to 18 October (8,400 rows) and weather has 5,139 rows. Running them on a schedule is a later step.

Then I built the first gold table, `gold_hourly`. Each row is one price area and one hour: the price, the total consumption (the five groups added together), the weather forecast made the day before, and the price for the same hour yesterday. I use the forecast from the day before because that is what a real forecast for tomorrow could know. A newer forecast would be cheating. The table only keeps hours that exist in all three sources, so for now it has 1,070 rows, from 10 to 18 October.

Last, I measured a simple baseline: use yesterday's price for the same hour. The mean absolute error, up to 18 October, is 0.234 NOK per kWh in NO1, 0.274 in NO2, 0.277 in NO3, 0.034 in NO4 and 0.203 in NO5. NO4 looks best, but its prices are also much lower. This is only nine days of data, so the numbers will change. The baseline fails most when the week changes: on Saturday 10 October the night price in NO1 was about 0.15, while the day before it was about 0.90. A model will need to know the day of the week to beat it.

### Day 12 (21 October 2026)

Both scheduled runs on 20 October were green as well, so the daily run has now worked seven full days without help, from 14 to 20 October.

Today I started the report side. I moved Power BI forward in my plan and used Power BI Desktop instead of Microsoft Fabric for now, because Desktop is free and runs on my own computer. I exported the gold table from Databricks as a CSV file with all 1,070 rows and loaded it with Power Query. I didn't refresh the layers first, so the data still ends on 18 October.

The first thing I found was a time trap. In Databricks the first row is NO1 at 05:00 UTC on 14 October, but the Power BI preview showed 07:00. Power BI had quietly turned the UTC times into my computer's local time. I kept the time zone when reading the column and then removed only the zone label, so 05:00 stays 05:00. To check, I counted the different hours: 214, the same as in the gold table. If I had missed this, the hours would have moved again when Norway changes its clock on 25 October. I also rounded consumption to whole kWh, because adding the five consumer groups had left tiny decimals like 3216954.2139999997.

Then I built a star schema. The fact table, `fact_hourly`, has the 1,070 hourly rows with price, consumption, weather and yesterday's price. Around it are two dimension tables: `dim_area`, with the five price areas and readable names like "North (Tromsø)", and `dim_date`, with the nine dates, the day of the week and a weekend flag. Four of the nine days are weekend days. I added the day of the week because of yesterday's baseline, which failed most on a Saturday. Both relationships are many-to-one, from the fact table to each dimension. Power BI found the area relationship by itself; the date relationship I made by hand.

The report file stays on my computer for now. I will add it here when the first page with DAX measures is ready.

## Data sources

- Electricity prices: Strømpriser levert av [Hva koster strømmen.no](https://www.hvakosterstrommen.no). They get the prices from ENTSO-E. Prices are without VAT.
- Electricity consumption: [Elhub](https://api.elhub.no), open Energy Data API. Hourly consumption per price area and consumer group.
- Weather forecast: Based on data from [MET Norway](https://api.met.no), Locationforecast API, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). One forecast point per price area.
