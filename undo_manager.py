"""Move-history management for Smart File Organizer."""

import os
import shutil


class UndoManager:
    """Manage completed file-move operations for undo support."""

    def __init__(self):
        self._history = []
        self._pending_operation = None

    def begin_operation(self):
        """Start collecting moves for a new, uncommitted operation."""
        self._pending_operation = []

    def record_move(self, original_path, new_path):
        """Add one successful move to the operation currently in progress."""
        if self._pending_operation is not None:
            self._pending_operation.append({
                "original_path": original_path,
                "new_path": new_path
            })

    def commit_operation(self):
        """Save the pending operation as one undoable history entry."""
        if self._pending_operation:
            self._history.append(self._pending_operation)

        self._pending_operation = None
        return self.can_undo()

    def discard_operation(self):
        """Discard an incomplete operation after organization fails."""
        self._pending_operation = None

    def can_undo(self):
        """Return whether at least one completed operation can be undone."""
        return bool(self._history)

    def undo_last_operation(self, progress_callback=None):
        """Restore the newest completed operation in reverse move order."""
        if not self.can_undo():
            raise RuntimeError("There is no completed operation to undo.")

        operation = self._history[-1]
        total_moves = len(operation)
        restored_moves = 0
        skipped_moves = 0
        remaining_moves = []

        for index, move in enumerate(reversed(operation), start=1):
            original_path = move["original_path"]
            new_path = move["new_path"]

            try:
                if not os.path.exists(new_path) or os.path.exists(original_path):
                    skipped_moves += 1
                    remaining_moves.append(move)
                else:
                    original_folder = os.path.dirname(original_path)
                    os.makedirs(original_folder, exist_ok=True)
                    shutil.move(new_path, original_path)
                    restored_moves += 1

            except (OSError, shutil.Error):
                skipped_moves += 1
                remaining_moves.append(move)

            if progress_callback:
                progress_callback(
                    index / total_moves,
                    restored_moves,
                    skipped_moves
                )

        if remaining_moves:
            self._history[-1] = list(reversed(remaining_moves))
        else:
            self._history.pop()

        return {
            "total": total_moves,
            "restored": restored_moves,
            "skipped": skipped_moves,
            "completed": not remaining_moves
        }
