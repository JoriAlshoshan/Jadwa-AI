from django.urls import path
from . import views

urlpatterns = [
    path("run/<int:project_id>/", views.run_analysis, name="run_analysis"),
    path("result/<int:result_id>/", views.analysis_result, name="analysis_result"),
    path("recs-loading/<int:result_id>/", views.recs_loading, name="recs_loading"),
    path("recs-status/<int:result_id>/", views.recs_status, name="recs_status"),
    path("recommend/<int:result_id>/", views.generate_recs, name="generate_recs"),
]
