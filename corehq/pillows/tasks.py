from celery.schedules import crontab
from celery.task import periodic_task

from corehq.apps.es import FormES
from corehq.form_processor.interfaces.dbaccessors import FormAccessors
from corehq.form_processor.utils.xform import resave_form
from corehq.pillows.utils import get_user_type_deep_cache_for_unknown_users
from corehq.util.datadog.gauges import datadog_gauge
from corehq.util.decorators import serial_task


@periodic_task(run_every=crontab(minute=0, hour=0))
def fix_user_types():
    unknown_user_ids = (
        FormES().user_type('unknown').user_aggregation().run().aggregations.user.keys
    )
    datadog_gauge('commcare.fix_user_types.unknown_user_count', len(unknown_user_ids))
    for user_id in unknown_user_ids:
        user_type = get_user_type_deep_cache_for_unknown_users(user_id)
        if user_type != unknown_user_ids:
            resave_es_forms_with_unknown_user_type.delay(user_id)


@serial_task('{user_id}', queue='background_queue')
def resave_es_forms_with_unknown_user_type(user_id):
    domain_form_id_list = (
        FormES().user_type('unknown').user_id(user_id)
        .values_list('domain', '_id', scroll=True)
    )
    for domain, form_id in domain_form_id_list:
        form = FormAccessors(domain).get_form(form_id)
        resave_form(domain, form)