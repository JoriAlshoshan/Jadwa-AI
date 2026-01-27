from django.urls import path
from . import views

urlpatterns = [
    path("run/<int:project_id>/", views.run_analysis, name="run_analysis"),
    path("result/<int:result_id>/", views.analysis_result, name="analysis_result"),
    path("recommend/<int:result_id>/", views.generate_recs, name="generate_recs"),
]
