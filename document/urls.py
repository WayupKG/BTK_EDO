from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateDocView.as_view(), name="create_doc"),
    path('create/statement/', views.CreateStatementRaportView.as_view(), name="create_statement"),

    path('inbox/', views.InboxDocView.as_view(), name="inbox_doc"),
    path('statement/inbox/', views.InboxStatView.as_view(), name="inbox_stat"),
    path('statement/inbox/dir/', views.InboxDirStatView.as_view(), name="inbox_dir"),

    path('inbox/detail/<slug:slug>/', views.InboxDocumentDetailView.as_view(), name="detail-doc-view"),
    path('statement/detail/<slug:slug>/', views.StatementDetailView.as_view(), name="detail-stat-view"),
    path('director/detail/<slug:slug>/', views.DirectorStatementDetailView.as_view(), name="detail-ditector-view"),

    path('shipped/', views.ShippedDocumentView.as_view(), name="shipped_doc"),
    path('stats/shipped/', views.ShippedStatView.as_view(), name="shipped_stat"),
    path('shipped/detail/<slug:slug>/', views.ShippedDocumentDetailView.as_view(), name="detail-shipped-view"),

    path('inbox/remove/<slug:slug>/doc/', views.remove_inbox_doc, name="remove_inbox_doc"),
    path('inbox/remove/<slug:slug>/stat/', views.remove_inbox_stat, name="remove_inbox_stat"),
    path('inbox/remove/<slug:slug>/dir/', views.remove_inbox_stat_director, name="remove_inbox_director"),

    path('statement/detail/<slug:slug>/pdf/', views.RenderPDFStatement.as_view(), name="render-statement-pdf"),
]
