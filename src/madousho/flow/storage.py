"""Storage layer for Madousho.ai Task system.

Provides atomic JSON writing, JSONL indexing, and flow/task persistence.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class AtomicJsonWriter:
    """Atomically write JSON data to file using tempfile + fsync + os.replace."""

    @staticmethod
    async def write(path: Path, data: Dict[str, Any]) -> None:
        """
        Write JSON data atomically to file.

        Args:
            path: Target file path
            data: Data to write as JSON

        Raises:
            IOError: If write fails
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=".tmp_",
            suffix=".json"
        )

        try:
            # Write to temporary file
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is on disk

            # Atomic replace
            os.replace(temp_path, path)

            # Fsync directory to ensure rename is persisted
            dir_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)

        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


class FlowIndex:
    """JSONL-based global index for all flows.

    Uses JSON Lines format for lazy loading - each line is a complete JSON object.
    """

    def __init__(self, base_dir: Path):
        """
        Initialize the flow index.

        Args:
            base_dir: Base directory for flow storage
        """
        self.base_dir = Path(base_dir)
        self.index_file = self.base_dir / "flows.jsonl"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def append_flow(self, flow_info: Dict[str, Any]) -> None:
        """
        Append a flow entry to the index.

        Args:
            flow_info: Flow metadata dict
        """
        async with self._lock:
            line = json.dumps(flow_info, ensure_ascii=False) + "\n"
            with open(self.index_file, 'a', encoding='utf-8') as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())

    async def list_flows(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List flows with pagination (lazy loading).

        Args:
            limit: Maximum number of flows to return
            offset: Number of flows to skip

        Returns:
            List of flow metadata dicts
        """
        if not self.index_file.exists():
            return []

        flows = []
        current_offset = 0

        with open(self.index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if current_offset < offset:
                    current_offset += 1
                    continue

                if len(flows) >= limit:
                    break  # Early exit - lazy loading

                line = line.strip()
                if line:
                    flows.append(json.loads(line))

        return flows

    async def update_flow(self, flow_uuid: str, updates: Dict[str, Any]) -> bool:
        """
        Update a flow entry in the index.

        Args:
            flow_uuid: UUID of flow to update
            updates: Fields to update

        Returns:
            True if flow was found and updated, False otherwise
        """
        async with self._lock:
            if not self.index_file.exists():
                return False

            # Read all flows
            flows = []
            found = False

            with open(self.index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        flow = json.loads(line)
                        if flow.get('uuid') == flow_uuid:
                            flow.update(updates)
                            found = True
                        flows.append(flow)

            if not found:
                return False

            # Rewrite entire file atomically
            fd, temp_path = tempfile.mkstemp(
                dir=self.base_dir,
                prefix=".tmp_",
                suffix=".jsonl"
            )

            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    for flow in flows:
                        f.write(json.dumps(flow, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

                os.replace(temp_path, self.index_file)
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise

            return True


class FlowStorage:
    """Storage layer for flow and task persistence.

    File structure:
        data/flow/
        ├── flows.jsonl              # Global index
        └── {flow_uuid}/
            ├── meta.json            # Flow metadata + task list
            └── {task_uuid}.json     # Individual task state
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize flow storage.

        Args:
            base_dir: Base directory for flow storage (default: data/flow)
        """
        self.base_dir = base_dir or Path("data/flow")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, asyncio.Lock] = {}
        self._index = FlowIndex(self.base_dir)

    def _get_lock(self, file_path: Path) -> asyncio.Lock:
        """Get or create a lock for a specific file."""
        key = str(file_path.resolve())
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def create_flow(
        self,
        uuid: str,
        name: str,
        description: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Create a new flow directory and metadata file.

        Args:
            uuid: Flow UUID
            name: Flow name
            description: Flow description
            context: Flow context data
        """
        flow_dir = self.base_dir / uuid
        flow_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "uuid": uuid,
            "name": name,
            "description": description,
            "context": context,
            "tasks": [],
            "created_at": self._timestamp()
        }

        meta_path = flow_dir / "meta.json"
        await AtomicJsonWriter.write(meta_path, meta)

        # Add to global index
        await self._index.append_flow({
            "uuid": uuid,
            "name": name,
            "description": description,
            "created_at": meta["created_at"]
        })

    async def register_task(
        self,
        task_id: str,
        label: Optional[str],
        flow_uuid: str,
        timeout: float = 30.0
    ) -> None:
        """
        Register a task in the flow's meta.json.

        Args:
            task_id: Task UUID
            label: Task label (optional, not unique)
            flow_uuid: Parent flow UUID
            timeout: Task timeout in seconds
        """
        meta_path = self.base_dir / flow_uuid / "meta.json"
        lock = self._get_lock(meta_path)

        async with lock:
            # Read current meta
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # Add task to index
            task_info = {
                "uuid": task_id,
                "label": label,
                "timeout": timeout,
                "state": "pending",
                "created_at": self._timestamp()
            }
            meta["tasks"].append(task_info)

            # Write back atomically
            await AtomicJsonWriter.write(meta_path, meta)

        # Create task state file
        task_path = self.base_dir / flow_uuid / f"{task_id}.json"
        task_state = {
            "uuid": task_id,
            "flow_uuid": flow_uuid,
            "label": label,
            "state": "pending",
            "timeout": timeout,
            "messages": [],
            "result": None,
            "error": None,
            "created_at": task_info["created_at"],
            "started_at": None,
            "completed_at": None
        }
        await AtomicJsonWriter.write(task_path, task_state)

    async def update_task_state(
        self,
        flow_uuid: str,
        task_id: str,
        state: str,
        result: Any = None,
        error: Optional[str] = None,
        messages: Optional[List[Dict]] = None
    ) -> None:
        """
        Update a task's state.

        Args:
            flow_uuid: Parent flow UUID
            task_id: Task UUID
            state: New state (pending|running|completed|failed)
            result: Task result (if completed)
            error: Error message (if failed)
            messages: OpenAI-style message history
        """
        task_path = self.base_dir / flow_uuid / f"{task_id}.json"
        meta_path = self.base_dir / flow_uuid / "meta.json"

        # Update task file
        async with self._get_lock(task_path):
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            task_data["state"] = state
            if result is not None:
                task_data["result"] = result
            if error is not None:
                task_data["error"] = error
            if messages is not None:
                task_data["messages"] = messages

            now = self._timestamp()
            if state == "running" and task_data["started_at"] is None:
                task_data["started_at"] = now
            if state in ("completed", "failed", "timeout"):
                task_data["completed_at"] = now

            await AtomicJsonWriter.write(task_path, task_data)

        # Update meta.json task index
        async with self._get_lock(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            for task_info in meta["tasks"]:
                if task_info["uuid"] == task_id:
                    task_info["state"] = state
                    break

            await AtomicJsonWriter.write(meta_path, meta)

    async def get_tasks(self, label: str, flow_uuid: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with matching label (flow-scoped).

        Args:
            label: Task label to search for
            flow_uuid: Parent flow UUID

        Returns:
            List of task data dicts (in registration order)
        """
        meta_path = self.base_dir / flow_uuid / "meta.json"

        # Read meta to get task list
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Find matching task UUIDs
        matching_uuids = [
            t["uuid"] for t in meta["tasks"]
            if t.get("label") == label
        ]

        # Load each task's full data
        tasks = []
        for task_id in matching_uuids:
            task_path = self.base_dir / flow_uuid / f"{task_id}.json"
            with open(task_path, 'r', encoding='utf-8') as f:
                tasks.append(json.load(f))

        return tasks

    async def recover_orphaned_tasks(self) -> int:
        """
        Recover orphaned tasks (running state but no started_at).

        Returns:
            Number of tasks recovered
        """
        recovered = 0

        if not self.base_dir.exists():
            return 0

        # Scan all flow directories
        for flow_dir in self.base_dir.iterdir():
            if not flow_dir.is_dir():
                continue

            meta_path = flow_dir / "meta.json"
            if not meta_path.exists():
                continue

            # Read flow metadata
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            flow_uuid = meta["uuid"]

            # Check each task
            for task_info in meta["tasks"]:
                if task_info["state"] != "running":
                    continue

                task_id = task_info["uuid"]
                task_path = flow_dir / f"{task_id}.json"

                if not task_path.exists():
                    continue

                # Read task state
                with open(task_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)

                # Orphaned: running but no started_at
                if task_data.get("started_at") is None:
                    # Mark as failed
                    task_data["state"] = "failed"
                    task_data["error"] = "Process crashed or was killed"
                    task_data["completed_at"] = self._timestamp()

                    await AtomicJsonWriter.write(task_path, task_data)

                    # Update meta
                    task_info["state"] = "failed"
                    await AtomicJsonWriter.write(meta_path, meta)

                    recovered += 1

        return recovered

    def _timestamp(self) -> str:
        """Get current UTC timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
