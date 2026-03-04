"""Unit tests for FlowStorage layer."""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from madousho.flow.storage import AtomicJsonWriter, FlowIndex, FlowStorage


class TestAtomicJsonWriter:
    """Tests for AtomicJsonWriter class."""
    
    @pytest.mark.asyncio
    async def test_write_creates_file(self):
        """Test that write creates the target file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_data = {"key": "value"}
            
            await AtomicJsonWriter.write(test_file, test_data)
            
            assert test_file.exists()
    
    @pytest.mark.asyncio
    async def test_write_content_correct(self):
        """Test that written content matches input data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
            
            await AtomicJsonWriter.write(test_file, test_data)
            
            with open(test_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            assert content == test_data
    
    @pytest.mark.asyncio
    async def test_write_creates_parent_directories(self):
        """Test that write creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "subdir" / "nested" / "test.json"
            test_data = {"key": "value"}
            
            await AtomicJsonWriter.write(test_file, test_data)
            
            assert test_file.exists()
            assert test_file.parent.exists()
    
    @pytest.mark.asyncio
    async def test_write_no_temp_files_remaining(self):
        """Test that no temporary files remain after successful write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_data = {"key": "value"}
            
            await AtomicJsonWriter.write(test_file, test_data)
            
            temp_files = list(Path(tmpdir).glob(".tmp_*"))
            assert len(temp_files) == 0
    
    @pytest.mark.asyncio
    async def test_write_cleanup_on_error(self):
        """Test that temporary files are cleaned up on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file to cause permission error
            test_file = Path(tmpdir) / "test.json"
            test_data = {"key": "value"}
            
            # Write once to create file
            await AtomicJsonWriter.write(test_file, test_data)
            
            # Make directory read-only to cause error
            import os
            os.chmod(tmpdir, 0o555)
            
            try:
                # Try to write again (should fail)
                with pytest.raises(Exception):
                    await AtomicJsonWriter.write(test_file, {"new": "data"})
                
                # No temp files should remain
                temp_files = list(Path(tmpdir).glob(".tmp_*"))
                assert len(temp_files) == 0
            finally:
                # Restore permissions for cleanup
                os.chmod(tmpdir, 0o755)


class TestFlowIndex:
    """Tests for FlowIndex class."""
    
    @pytest.mark.asyncio
    async def test_append_flow_creates_index(self):
        """Test that append_flow creates the index file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            await index.append_flow({
                "uuid": "test-uuid",
                "name": "test_flow"
            })
            
            assert index.index_file.exists()
    
    @pytest.mark.asyncio
    async def test_list_flows_empty(self):
        """Test that list_flows returns empty list when no flows."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            flows = await index.list_flows()
            
            assert flows == []
    
    @pytest.mark.asyncio
    async def test_list_flows_with_data(self):
        """Test that list_flows returns flows in order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            # Add 3 flows
            for i in range(3):
                await index.append_flow({
                    "uuid": f"flow-{i}",
                    "name": f"Flow {i}"
                })
            
            flows = await index.list_flows()
            
            assert len(flows) == 3
            assert flows[0]["uuid"] == "flow-0"
            assert flows[2]["uuid"] == "flow-2"
    
    @pytest.mark.asyncio
    async def test_list_flows_pagination(self):
        """Test that list_flows supports pagination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            # Add 10 flows
            for i in range(10):
                await index.append_flow({
                    "uuid": f"flow-{i:02d}",
                    "name": f"Flow {i}"
                })
            
            # Page 1: limit=3, offset=0
            page1 = await index.list_flows(limit=3, offset=0)
            assert len(page1) == 3
            assert page1[0]["uuid"] == "flow-00"
            
            # Page 2: limit=3, offset=3
            page2 = await index.list_flows(limit=3, offset=3)
            assert len(page2) == 3
            assert page2[0]["uuid"] == "flow-03"
            
            # Last page: should have 1 flow
            last_page = await index.list_flows(limit=3, offset=9)
            assert len(last_page) == 1
    
    @pytest.mark.asyncio
    async def test_update_flow_found(self):
        """Test that update_flow returns True when flow exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            await index.append_flow({
                "uuid": "test-uuid",
                "name": "test_flow"
            })
            
            result = await index.update_flow("test-uuid", {"updated": True})
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_update_flow_not_found(self):
        """Test that update_flow returns False when flow doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = FlowIndex(Path(tmpdir))
            
            result = await index.update_flow("nonexistent", {"updated": True})
            
            assert result is False


class TestFlowStorage:
    """Tests for FlowStorage class."""
    
    @pytest.mark.asyncio
    async def test_init_creates_base_dir(self):
        """Test that __init__ creates the base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / "flow_storage"
            storage = FlowStorage(base_dir)
            
            assert storage.base_dir.exists()
    
    @pytest.mark.asyncio
    async def test_create_flow_creates_directory(self):
        """Test that create_flow creates flow directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(
                uuid="test-flow-uuid",
                name="test_flow",
                description="A test flow",
                context={"key": "value"}
            )
            
            flow_dir = Path(tmpdir) / "test-flow-uuid"
            assert flow_dir.exists()
    
    @pytest.mark.asyncio
    async def test_create_flow_creates_meta_json(self):
        """Test that create_flow creates meta.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(
                uuid="test-flow-uuid",
                name="test_flow",
                description="A test flow",
                context={"key": "value"}
            )
            
            meta_path = Path(tmpdir) / "test-flow-uuid" / "meta.json"
            assert meta_path.exists()
            
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            assert meta["name"] == "test_flow"
            assert meta["description"] == "A test flow"
            assert meta["context"] == {"key": "value"}
            assert meta["tasks"] == []
    
    @pytest.mark.asyncio
    async def test_register_task_adds_to_meta(self):
        """Test that register_task adds task to meta.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(
                uuid="test-flow",
                name="test_flow",
                description="",
                context={}
            )
            
            await storage.register_task(
                task_id="task-uuid",
                label="test_label",
                flow_uuid="test-flow",
                timeout=30.0
            )
            
            meta_path = Path(tmpdir) / "test-flow" / "meta.json"
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            assert len(meta["tasks"]) == 1
            assert meta["tasks"][0]["uuid"] == "task-uuid"
            assert meta["tasks"][0]["label"] == "test_label"
    
    @pytest.mark.asyncio
    async def test_register_task_creates_task_file(self):
        """Test that register_task creates task state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(
                uuid="test-flow",
                name="test_flow",
                description="",
                context={}
            )
            
            await storage.register_task(
                task_id="task-uuid",
                label="test_label",
                flow_uuid="test-flow",
                timeout=30.0
            )
            
            task_path = Path(tmpdir) / "test-flow" / "task-uuid.json"
            assert task_path.exists()
            
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            assert task_data["uuid"] == "task-uuid"
            assert task_data["label"] == "test_label"
            assert task_data["state"] == "pending"
    
    @pytest.mark.asyncio
    async def test_update_task_state_changes_status(self):
        """Test that update_task_state updates task status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            await storage.register_task("task-uuid", "test", "test-flow")
            
            # Update to running
            await storage.update_task_state(
                flow_uuid="test-flow",
                task_id="task-uuid",
                state="running"
            )
            
            task_path = Path(tmpdir) / "test-flow" / "task-uuid.json"
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            assert task_data["state"] == "running"
            assert task_data["started_at"] is not None
    
    @pytest.mark.asyncio
    async def test_update_task_state_with_result(self):
        """Test that update_task_state saves result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            await storage.register_task("task-uuid", "test", "test-flow")
            
            result_data = {"output": "success", "value": 42}
            
            await storage.update_task_state(
                flow_uuid="test-flow",
                task_id="task-uuid",
                state="completed",
                result=result_data
            )
            
            task_path = Path(tmpdir) / "test-flow" / "task-uuid.json"
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            assert task_data["state"] == "completed"
            assert task_data["result"] == result_data
    
    @pytest.mark.asyncio
    async def test_get_tasks_returns_matching_label(self):
        """Test that get_tasks returns tasks with matching label."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            
            # Register tasks with different labels
            await storage.register_task("task-1", "search", "test-flow")
            await storage.register_task("task-2", "search", "test-flow")
            await storage.register_task("task-3", "fetch", "test-flow")
            
            # Get search tasks
            search_tasks = await storage.get_tasks("search", "test-flow")
            assert len(search_tasks) == 2
            
            # Get fetch tasks
            fetch_tasks = await storage.get_tasks("fetch", "test-flow")
            assert len(fetch_tasks) == 1
    
    @pytest.mark.asyncio
    async def test_get_tasks_returns_in_registration_order(self):
        """Test that get_tasks returns tasks in registration order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            
            await storage.register_task("task-1", "same", "test-flow")
            await storage.register_task("task-2", "same", "test-flow")
            await storage.register_task("task-3", "same", "test-flow")
            
            tasks = await storage.get_tasks("same", "test-flow")
            
            assert tasks[0]["uuid"] == "task-1"
            assert tasks[1]["uuid"] == "task-2"
            assert tasks[2]["uuid"] == "task-3"
    
    @pytest.mark.asyncio
    async def test_recover_orphaned_tasks(self):
        """Test that recover_orphaned_tasks marks orphaned tasks as failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            await storage.register_task("orphan-task", "test", "test-flow")
            
            # Manually set state to running without started_at (simulate crash)
            task_path = Path(tmpdir) / "test-flow" / "orphan-task.json"
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            task_data["state"] = "running"
            task_data["started_at"] = None
            
            with open(task_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f)
            
            # Also update meta.json
            meta_path = Path(tmpdir) / "test-flow" / "meta.json"
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            for t in meta["tasks"]:
                if t["uuid"] == "orphan-task":
                    t["state"] = "running"
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f)
            
            # Recover orphaned tasks
            recovered = await storage.recover_orphaned_tasks()
            
            assert recovered == 1
            
            # Verify task is now failed
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            assert task_data["state"] == "failed"
            assert task_data["error"] is not None
            assert "crashed" in task_data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_recover_orphaned_tasks_ignores_normal_tasks(self):
        """Test that recover_orphaned_tasks doesn't affect normal tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FlowStorage(Path(tmpdir))
            
            await storage.create_flow(uuid="test-flow", name="test", description="", context={})
            await storage.register_task("normal-task", "test", "test-flow")
            
            # Set state to completed (normal)
            await storage.update_task_state(
                flow_uuid="test-flow",
                task_id="normal-task",
                state="completed",
                result={"done": True}
            )
            
            # Recover should not affect completed tasks
            recovered = await storage.recover_orphaned_tasks()
            
            assert recovered == 0
            
            # Verify task is still completed
            tasks = await storage.get_tasks("test", "test-flow")
            assert tasks[0]["state"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
