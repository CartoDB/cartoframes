"""Batch SQL API functionality for longer running operations"""
from carto.sql import BatchSQLClient

class BatchJobStatus(object):
    """Status of a write or query operation. Read more at `Batch SQL API docs
    <https://carto.com/docs/carto-engine/sql-api/batch-queries/>`__ about
    responses and how to interpret them.

    Example:

        Poll for a job's status if you've caught the :py:class:`BatchJobStatus`
        instance.

        .. code:: python

            import time
            job = cc.write(df, 'new_table',
                           lnglat=('lng_col', 'lat_col'))
            while True:
                curr_status = job.status()['status']
                if curr_status in ('done', 'failed', 'canceled', 'unknown', ):
                    print(curr_status)
                    break
                time.sleep(5)

        Create a :py:class:`BatchJobStatus` instance if you have a `job_id`
        output from a :py:meth:`CartoContext.write
        <cartoframes.context.CartoContext.write>` operation.

        .. code:: python

            >>> from cartoframes import CartoContext, BatchJobStatus
            >>> cc = CartoContext(username='...', api_key='...')
            >>> cc.write(df, 'new_table', lnglat=('lng', 'lat'))
            'BatchJobStatus(job_id='job-id-string', ...)'
            >>> batch_job = BatchJobStatus(cc, 'job-id-string')

    Attributes:
        job_id (str): Job ID of the Batch SQL API job
        last_status (str): Status of ``job_id`` job when last polled
        created_at (str): Time and date when job was created

    Args:
        carto_context (:py:class:`CartoContext <cartoframes.context.CartoContext>`):
          :py:class:`CartoContext <cartoframes.context.CartoContext>` instance
        job (dict or str): If a dict, job status dict returned after sending
            a Batch SQL API request. If str, a Batch SQL API job id.
    """
    def __init__(self, carto_context, job):
        if isinstance(job, dict):
            self.job_id = job.get('job_id')
            self.last_status = job.get('status')
            self.created_at = job.get('created_at')
        elif isinstance(job, str):
            self.job_id = job
            self.last_status = None
            self.created_at = None

        self._batch_client = BatchSQLClient(carto_context.auth_client)

    def __repr__(self):
        return ('BatchJobStatus(job_id=\'{job_id}\', '
                'last_status=\'{status}\', '
                'created_at=\'{created_at}\')'.format(
                    job_id=self.job_id,
                    status=self.last_status,
                    created_at=self.created_at))

    def _set_status(self, curr_status):
        self.last_status = curr_status

    def get_status(self):
        """return current status of job"""
        return self.last_status

    def status(self):
        """Checks the current status of job ``job_id``

        Returns:
            dict: Status and time it was updated

        Warns:
            UserWarning: If the job failed, a warning is raised with
                information about the failure
        """
        resp = self._batch_client.read(self.job_id)
        if 'failed_reason' in resp:
            warn('Job failed: {}'.format(resp.get('failed_reason')))
        self._set_status(resp.get('status'))
        return dict(status=resp.get('status'),
                    updated_at=resp.get('updated_at'),
                    created_at=resp.get('created_at'))
