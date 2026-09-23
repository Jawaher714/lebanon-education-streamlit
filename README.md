# Education across Lebanon

A Streamlit app for MSBA 325, based on the dropout histogram and illiteracy/dropout scatter plot in the supplied Plotly assignment.

**Public app link:** Pending deployment to Streamlit Community Cloud. Replace this line with the verified public URL after deployment.

## Features
- Two interactive Plotly charts with linked area and town filters.
- Two calculated full-dataset insights plus summaries for the current selection.
- Widget and chart design justifications in an on-page expander.
- Missing-data disclosure, invalid-percentage handling, source notes and a filtered CSV download.

## Run locally
Use Python 3.12 or 3.13. Open this folder in VS Code, then run:

```shell
python -m venv .venv
```

Windows PowerShell (activation is not required):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS/Linux:

```shell
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository and upload this folder's contents, including `app.py`, `requirements.txt`, `education.csv` and `.streamlit/config.toml`. Keep the folder structure.
2. Sign in at https://share.streamlit.io and choose **Create app** / **Deploy a public app from GitHub**.
3. Select the repository, its branch (usually `main`), and main file `app.py`.
4. In advanced settings, use Python 3.12 or 3.13. Deploy and wait for the app to load.
5. Verify the app is public and opens when signed out. Copy its `https://...streamlit.app` URL into this README and commit it.

## Data and interpretation
`education.csv` is an unchanged copy of `9a5d5d78f2f1e8bacbf858385cb6f5fa_20240905_122326.csv` supplied for the assignment. Publisher: Impact Open Data, via AUB CODEC. Dataset identifier: http://linked.aub.edu.lb/CODEC/Lebanon/Dataset/Educational_Level-Lebanon-2023. Source portal: https://impact.cib.gov.lb/home#open_data_section.

The app uses the education dataset for both charts; the water file is unnecessary for this pair. Percentages outside 0–100 are excluded per measure, missing values are not imputed, and correlations use complete pairs. Areas preserve the source's mixed district/governorate labels. Towns receive equal weight; these are not national population estimates. Correlation does not imply causation.

## Assignment coverage
1. **Data and visualizations:** original assignment slides 3–4, context and two calculated insights.
2. **Linked interactions:** area dropdown updates the town multiselect's options and clears stale choices; both filter both charts.
3. **Design justification:** an expander explains user questions, alternatives and course concepts for each widget.
4. **Deployment:** repository files are prepared; completion requires the verified public app link above.
