# Supply Chain Delivery Performance Analysis

## Project overview

This project analyzes shipment delivery data using Python. It examines delivery timeliness, delays, carriers, routes, destination regions, shipping modes, delay reasons, and monthly trends.

The included dataset is synthetic and intended for learning and demonstration. It contains more than 5,000 shipment records.

## Project structure

```text
supply_chain_delivery_analysis/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   │   └── shipment_delivery.csv
│   └── processed/
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── analysis.py
│   ├── visualization.py
│   └── utils.py
└── outputs/
```

## Setup and run

Use Python 3.9 or newer.

1. Open a terminal in the project folder.
2. Install the required packages:

   ```text
   python -m pip install -r requirements.txt
   ```

3. Confirm the raw CSV is located at:

   ```text
   data/raw/shipment_delivery.csv
   ```

4. Run the analysis pipeline:

   ```text
   python main.py
   ```

5. Launch the interactive Streamlit dashboard:

   ```text
   streamlit run app.py
   ```

## Streamlit Cloud Deployment

To deploy this dashboard live on **Streamlit Community Cloud** (free):
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"**.
4. Select your repository, set the Branch to `main` (or `master`), and set Main file path to `app.py`.
5. Click **"Deploy"**. The app will install packages from `requirements.txt` and launch automatically.

## Data cleaning and metric definitions

The analysis removes duplicate shipment IDs, standardizes category values, converts date and numeric columns, and rebuilds each route from its origin and destination.

Cancelled and in-transit shipments are excluded from delivery-outcome KPIs. Delivered shipments without valid dispatch, expected-delivery, or actual-delivery dates are kept in the cleaned data but excluded from those KPIs. Date sequences that place dispatch before the order, or expected delivery before dispatch, are treated as invalid.

- **Delivery_Days**: actual delivery date minus ship date, in days.
- **Delay_Days**: actual delivery date minus expected delivery date, in days. A negative value means early delivery; zero means on time; a positive value means late.
- **On_Time**: 1 when delivered on or before the expected date; otherwise 0.
- **Outcome_Eligible**: identifies delivered shipments with valid dates for outcome analysis.

Carrier and route watchlists require at least 20 eligible shipments. This minimum-volume threshold helps avoid ranking groups based on very small samples. The comparisons are descriptive and do not prove that a carrier or route caused a delay.

## Analysis and outputs

Running `main.py` saves the cleaned dataset under `data/processed/` and writes KPI, carrier, route, region, delay-reason, shipping-mode, monthly-trend, and data-quality summaries under `outputs/`.

It also creates delivery-performance charts and a business findings report in `outputs/`. Monthly trend analysis is included when the data covers more than one month.

## Limitations

The dataset is synthetic, so findings demonstrate an analysis workflow and should not be treated as evidence about a real logistics operation. Additional information—such as warehouse release times, weather, customs events, delivery attempts, and service-level commitments—would help explain real-world delays.