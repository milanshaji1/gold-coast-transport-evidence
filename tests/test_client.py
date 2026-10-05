import asyncio
import pytest
from transport.client import call_tools

@pytest.mark.parametrize('calls', [[],[{'name':'quality_provenance'}]*7,[{'name':'execute_sql','arguments':{'sql':'DROP'}}]])
def test_client_refuses_empty_over_budget_and_unknown_tools(calls):
    with pytest.raises(ValueError): asyncio.run(call_tools(calls))
