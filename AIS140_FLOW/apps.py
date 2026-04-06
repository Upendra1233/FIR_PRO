from django.apps import AppConfig

class Ais140FlowConfig(AppConfig):
    name = 'AIS140_FLOW'

    def ready(self):
        # Guard sqlite3 datetime converter against None values returned by the DB
        try:
            import django.db.backends.sqlite3.operations as ops
            original = getattr(ops, 'convert_datetimefield_value', None)
            if original:
                def safe_convert_datetimefield_value(value, expression, connection):
                    if value is None:
                        return None
                    try:
                        return original(value, expression, connection)
                    except Exception:
                        return None
                ops.convert_datetimefield_value = safe_convert_datetimefield_value
        except Exception:
            pass