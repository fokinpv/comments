from concurrent.futures import ProcessPoolExecutor

from .tasks import create_snapshot


class Worker:

    def __init__(self, database_url, snapshots_dir):
        self.database_url = database_url
        self.snapshots_dir = snapshots_dir

    def _run_task(self, func, *args, **kwargs):
        with ProcessPoolExecutor() as executor:
            executor.submit(func, *args, **kwargs)

    def create_snapshot(self, snapshot_id, source, from_datetime, to_datetime):
        self._run_task(
            create_snapshot, self.database_url, self.snapshots_dir,
            snapshot_id, source,
            from_datetime, to_datetime
        )
