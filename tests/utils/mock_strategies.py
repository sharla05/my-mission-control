def mock_tstat_evaluator(log_entry):
    return "RED HIGH"


def mock_batt_evaluator(log_entry):
    return "RED LOW"


evaluation_strategy_map = {
    "TSTAT": mock_tstat_evaluator,
    "BATT": mock_batt_evaluator,
}
