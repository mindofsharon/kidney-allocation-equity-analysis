# kidney-allocation-equity-analysis

## Description 

A data analysis project exploring equity disparties and when they emerge in the kidney transplant waitlist pipeline. 

**Key aspects:**
- Waitlist outcome logistic regression model
- Time-to-transplant Cox proportional hazards model
- Fairness and disparty comparison metrics

## Local virtual enviornment setup

Create and activate virtual enviornment and install dependencies.
    
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Local data setup

In order to handle large CSV files which should not be uploaded to Github, use a local `data/` folder or set `DATA_DIR` to a custom path such as DATA_DIR=./path/to/local/data

1. Create a local data directory

2. Add the required files locally:
   - `data/cand_kipa.csv`
   - `data/tx_ki.csv`

3. Run test.py
