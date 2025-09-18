import re
from database.services.safety_decision_service import compute_request_hash, compute_record_hash

def test_compute_request_hash_deterministic():
    h1 = compute_request_hash(
        input_content="hello",
        response_content="world",
        content_type="general_question",
        user_id="11111111-1111-1111-1111-111111111111",
        session_id="22222222-2222-2222-2222-222222222222",
        applied_filters=["min_confidence", "keyword_filter"],
    )
    h2 = compute_request_hash(
        input_content="hello",
        response_content="world",
        content_type="general_question",
        user_id="11111111-1111-1111-1111-111111111111",
        session_id="22222222-2222-2222-2222-222222222222",
        applied_filters=["min_confidence", "keyword_filter"],
    )
    assert h1 == h2
    assert re.fullmatch(r"[0-9a-f]{64}", h1)

def test_compute_record_hash_chain_changes_with_prev():
    base_payload = {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "org_id": "org-1",
        "business_profile_id": None,
        "user_id": "11111111-1111-1111-1111-111111111111",
        "conversation_id": None,
        "content_type": "general_question",
        "decision": "allow",
        "confidence": 0.9,
        "applied_filters": [],
        "request_hash": "0"*64,
        "created_at": "2024-01-01T00:00:00Z",
        "metadata": {"k": "v"},
    }
    r1 = compute_record_hash(base_payload, prev_hash=None)
    r2 = compute_record_hash(base_payload, prev_hash=r1)
    assert r1 != r2
    assert re.fullmatch(r"[0-9a-f]{64}", r1)
    assert re.fullmatch(r"[0-9a-f]{64}", r2)