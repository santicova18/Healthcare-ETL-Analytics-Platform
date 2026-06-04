from django.apps import AppConfig

def ready(self):
    import apps.patients.signals

class PatientsConfig(AppConfig):
    name = 'apps.patients'
