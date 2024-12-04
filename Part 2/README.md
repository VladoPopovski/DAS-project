Step 1: scrape the data.
This step stores all issuer historical data in excel spreadsheets, which are later used to read from for the app.
After all data is downloaded the next step starts

Step 2: put the data folder in the app (Part 2) folder.

Step 3: run this in (pycharm) terminal where the folder is:
python -c "from app import create_app; app = create_app(); app.run(debug=True, port=5000)"

now the application is active and we can fetch the data, so we go to the last step.

step 4: run Visualization.py to open the website
the link will be in terminal
