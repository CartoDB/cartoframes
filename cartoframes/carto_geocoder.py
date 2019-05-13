def _datetime_to_cron(datetime):
    '{minute} {hour} {day} {month} * {year}'.format(
        minute = datetime.minute,
        hour = datetime.hour,
        day = datetime.day,
        month = datetime.month,
        year = datetime.year
    )

class CartoGeocoder:
    def __init__(
        self,
        cc,
        dataset,
        street,
        city=None, state=None, country=None, metadata=None
    ):
        self.job = cc.analysis_api().job_by_name('carto-geocoder')
        self.params = {
            'dataset': dataset,
            'street': street,
            'city': city,
            'country': country,
            'metadata': metadata
        }

    def preview(self, verbose=False):
        dry_params = {**self.params, 'dry': True}
        return self.job.execute_and_get_output(dry_params, verbose=verbose, decodeJson=True)

    def run(self, verbose=False):
        return self.job.execute_and_get_output(self.params, verbose=verbose, decodeJson=True)

    def run_periodically(self, cron_expr):
        return self.job.execute(self.params, decodeJson=True, schedule=cron_expr)

    def run_at(self, datetime):
        cron_expr = _datetime_to_cron(datetime)
        return self.run_periodically(cron_expr, verbose)

    def run_on_table_changes(self, tablename):
        return self.job.execute(self.params, table=tablename)

    def last_geocoding(self, schedule):
        def filter(exec):
            return exec.finished() and exec.success() and (exec.output(decodeJson=True) or {}).get('updated_rows', 0) > 0
        outputs = schedule.last_outputs(n=1, filter=filter)
        return outputs[0] if len(outputs) > 0 else None
