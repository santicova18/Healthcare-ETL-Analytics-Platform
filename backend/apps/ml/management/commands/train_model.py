from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Entrena el modelo de riesgo clínico'

    def handle(self, *args, **options):
        try:
            from apps.ml.train import train_risk_model
            resultado = train_risk_model()
            if resultado is None:
                self.stdout.write(self.style.ERROR('Error: No se recibió resultado del entrenamiento'))
            else:
                self.stdout.write(self.style.SUCCESS('\u2713 ' + str(resultado)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante el entrenamiento: {str(e)}'))