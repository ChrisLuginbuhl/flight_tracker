# flight_tracker
Uses Google Sheets and Tequila/Kiwi API to check a list of cities for flight prices below a threshold. Python 3. 100 Days of Code

This program implements the Day 39 problem in 100 Days of Code (written without referring to their solution). Reads a list of cities from a google spreadsheet, looks up IATA codes for those cities if any are missing, and searches for flights according to serach parameters in constants below. Results for most recent search saved in log file (around 10Mb if searching for 30 days)  If any results that are below the price threshold, a notification is sent via SMS (Twilio). API keys for Twilio, Sheety and Tequila are needed, put them in a credentials.py file or use environment variables.

Features that could be added:
-Email notifier
-if no direct flights found, search for flights with one stop
-other search parameters could go in spreadsheet or a GUI
-scheduler
