# Norway power market platform

A small data project about hourly electricity prices in Norway, built on Azure. I add to it step by step and write down what I have done.

## Status

- [x] Day 1: Azure storage basics and first sample of real price data
- [ ] Daily ingestion with Python
- [ ] Lakehouse layers in Microsoft Fabric
- [ ] Power BI dashboard
- [ ] Forecasting and anomaly detection in Databricks


## Done so far

### Day 1 (5 October 2026)

I created a resource group, put a storage account in it, and made a container for my files. Then I uploaded one day of price data for the Oslo area (NO1).

The part I liked most: I tried to open the file with only its URL, and Azure refused, because public access is turned off by default. Then I created a SAS token, which is a temporary, read-only key, and the same file opened. Seeing it fail first made the security model much easier to understand.

At the end I deleted the whole resource group, so nothing keeps running and costing money.

## Data sources

- Electricity prices: Strømpriser levert av [Hva koster strømmen.no](https://www.hvakosterstrommen.no). They get the prices from ENTSO-E. Prices are without VAT.
