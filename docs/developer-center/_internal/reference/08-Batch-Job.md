
BatchJobStatus[¶](#batchjobstatus "Permalink to this headline")
---------------------------------------------------------------

_class_ `cartoframes.context.``BatchJobStatus`(_carto_context_, _job_)

Status of a write or query operation. Read more at [Batch SQL API docs](https://carto.com/docs/carto-engine/sql-api/batch-queries/) about responses and how to interpret them.

Example

Poll for a job’s status if you’ve caught the [`BatchJobStatus`](cartoframes.context.html#cartoframes.context.BatchJobStatus "cartoframes.context.BatchJobStatus") instance.

import time
job = cc.write(df, 'new_table',
               lnglat=('lng_col', 'lat_col'))
while True:
    curr_status = job.status()\['status'\]
    if curr_status in ('done', 'failed', 'canceled', 'unknown', ):
        print(curr_status)
        break
    time.sleep(5)

Create a [`BatchJobStatus`](cartoframes.context.html#cartoframes.context.BatchJobStatus "cartoframes.context.BatchJobStatus") instance if you have a job_id output from a cc.write operation.

>>\> from cartoframes import CartoContext, BatchJobStatus
>>\> cc = CartoContext(username='...', api_key='...')
>>\> cc.write(df, 'new_table', lnglat=('lng', 'lat'))
'BatchJobStatus(job_id='job-id-string', ...)'
>>\> batch_job = BatchJobStatus(cc, 'job-id-string')

Attrs:

job\_id (str): Job ID of the Batch SQL API job last\_status (str): Status of `job_id` job when last polled created_at (str): Time and date when job was created



Parameters:

*   **carto_context** (_carto.CartoContext_) – CartoContext instance
*   **job** (_dict_ _or_ _str_) – If a dict, job status dict returned after sending a Batch SQL API request. If str, a Batch SQL API job id.

`get_status`()

return current status of job

`status`()

Checks the current status of job `job_id`



Returns:

Status and time it was updated

Return type:

dict

Warns:

**UserWarning** – If the job failed, a warning is raised with information about the failure

