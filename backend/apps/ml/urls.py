from django.urls import path

from apps.ml.views import (
    predicciones_single,
    model_info,
    model_versions,
    train_model,
)

urlpatterns = [
    path("predicciones/", predicciones_single, name="predicciones"),
    path("model-info/", model_info, name="model-info"),
    path("model-versions/", model_versions, name="model-versions"),
    path("train/", train_model, name="train-model"),
]



