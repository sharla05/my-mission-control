uv venv --python 3.13

uv lock

uv add fastapi uvicorn structlog python-multipart tomli

uv add pytest pytest-cov httpx pre-commit ruff isort pyright bandit --dev

input format
<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>


violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT        <-
violation lines:  2018-01-01 23:01:38.001000 1000 101 98 25 20 102.9 TSTAT  <-
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:03:03.008000 1000 101 98 25 20 102.7 TSTAT
violation lines:  2018-01-01 23:03:05.009000 1000 101 98 25 20 101.2 TSTAT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT
violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT

violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT        <-
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT

violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT


violation lines:  2018-01-01 23:01:38.001000 1000 101 98 25 20 102.9 TSTAT  <-
violation lines:  2018-01-01 23:03:03.008000 1000 101 98 25 20 102.7 TSTAT
violation lines:  2018-01-01 23:03:05.009000 1000 101 98 25 20 101.2 TSTAT

=================== battery only ======================
violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT
violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT
