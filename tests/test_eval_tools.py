from transport.eval_tools import response_error

def test_mcp_v2_error_flag_is_recognised():
    assert response_error({'is_error':True}) is True
    assert response_error({'is_error':False}) is False
