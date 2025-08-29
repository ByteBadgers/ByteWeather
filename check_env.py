import os
from dotenv import load_dotenv, dotenv_values

# Load with override just in case
load_dotenv(override=True)

# Print what dotenv sees directly
print("dotenv_values():", dotenv_values())

# Print what os.getenv sees
print("os.getenv:", os.getenv("OPENWEATHER_KEY"))

# Print the raw environment variables
print("os.environ.get:", os.environ.get("OPENWEATHER_KEY"))
