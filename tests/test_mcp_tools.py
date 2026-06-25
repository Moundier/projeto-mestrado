import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_server import (
    get_caol_step,
    submit_dispatch,
    get_audit_log,
    AUDIT_LOG,
)


class TestGetCaolStep:
    async def test_draft_step(self):
        result = await get_caol_step("draft", user_id="test")
        data = json.loads(result)
        assert data["status"] == "Rascunho inicial sendo preenchido"

    async def test_submitted_step(self):
        result = await get_caol_step("submitted", user_id="test")
        data = json.loads(result)
        assert data["status"] == "Submetido para análise documental"

    async def test_approved_step(self):
        result = await get_caol_step("approved", user_id="test")
        data = json.loads(result)
        assert data["status"] == "Aprovado"

    async def test_rejected_step(self):
        result = await get_caol_step("rejected", user_id="test")
        data = json.loads(result)
        assert data["status"] == "Rejeitado"

    async def test_unknown_step(self):
        result = await get_caol_step("nonexistent", user_id="test")
        data = json.loads(result)
        assert data["status"] == "Unknown step"


class TestSubmitDispatch:
    async def test_requires_human_confirmation(self):
        result = await submit_dispatch({"uuid": "abc"}, user_id="test", confirmed=False)
        data = json.loads(result)
        assert "error" in data
        assert "Human confirmation required" in data["error"]

    async def test_submit_success(self):
        result = await submit_dispatch({"uuid": "abc"}, user_id="test", confirmed=True)
        data = json.loads(result)
        assert data["message"] == "Dispatch submitted successfully"
        assert data["uuid"] == "abc"

    async def test_new_case_without_uuid(self):
        result = await submit_dispatch({"product": "test"}, user_id="test", confirmed=True)
        data = json.loads(result)
        assert data["uuid"] == "new"


class TestGetAuditLog:
    async def test_unauthorized(self):
        result = await get_audit_log(user_id="analyst")
        data = json.loads(result)
        assert "error" in data
        assert "Unauthorized" in data["error"]

    async def test_admin_returns_list(self):
        AUDIT_LOG.clear()
        result = await get_audit_log(user_id="admin")
        data = json.loads(result)
        assert isinstance(data, list)
