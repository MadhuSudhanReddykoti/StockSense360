# 📦 StockSense360 — Retail Replenishment Control Tower
> Turning historical Walmart sales data into smart reorder decisions using forecasting, priority scoring, and an interactive dashboard.
---
## 🚨 The Problem
Retail loses money in two ways:
- **Stockouts** → empty shelves → lost sales → unhappy customers
- **Overstock** → too much inventory → holding costs → waste
StockSense360 solves this by predicting demand and telling ops teams exactly **what to order, how much, and why** — before the shelf goes empty.
---
## 🏗️ What I Built
| Component | Description |
|---|---|
| **ETL Pipeline** | Converted M5 wide-format data into star-schema fact/dim tables |
| **Reorder Logic** | Safety stock, reorder point, order-up-to policy |
| **14-Day Forecast** | Seasonal naive baseline forecast per SKU |
| **Priority Score** | 0–100 urgency score per SKU (shortage gap + order qty + stockout risk) |
| **Power BI Dashboard** | Executive Overview + Control Tower Action List |
| **Streamlit Web App** | Interactive app with filters, charts, priority cards |
---
## 📊 Dataset
**Kaggle M5 Forecasting — Accuracy** (Walmart-style retail)
- Daily unit sales per store and item
- Calendar mapping
- Store/week prices
- Pilot: Store CA_1 · 41 SKUs
---
## 🛠️ Tools Used
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Power BI](https://img.shields.io/badge/PowerBI-F2C811?style=flat&logo=powerbi&logoColor=black)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)
---
## 📁 Project Structure


---
## 🚀 How to Run the App
```bash
# 1. Clone the repo
git clone https://github.com/MadhuSudhanReddykoti/StockSense360.git
cd StockSense360/06_app
# 2. Install dependencies
pip install streamlit plotly pandas
# 3. Add fact_sales.csv to 06_app folder (too large for GitHub)
# Download from Kaggle M5 dataset
# 4. Run the app
streamlit run app.py
```
---
## 📈 Key Results
- **23 SKUs** identified as needing reorder out of 41 pilot SKUs
- **1 High priority** item (FOODS_1_183 — score 83.5/100)
- **149 total units** recommended for reorder
- **14-day forecast** generated per SKU using seasonal naive approach
---
## 🔮 Future Work
- [ ] Deploy on Streamlit Cloud (free live URL)
- [ ] Auto-refresh with live data pipeline
- [ ] Email alerts for critical stock levels
- [ ] Scale to all 10 stores and full SKU catalog
- [ ] ML-based forecasting (XGBoost, Prophet)
---
## 👤 Author
**Madhu Sudhan Reddy Koti**
- GitHub: [@MadhuSudhanReddykoti](https://github.com/MadhuSudhanReddykoti)
