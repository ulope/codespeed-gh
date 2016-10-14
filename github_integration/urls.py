from django.conf.urls import url

from github_integration.views import webhook, TargetStatusView


urlpatterns = [
    url(r"webhook/$", webhook),
    url(r"status/(?P<repo_name>[a-zA-Z_./-]+)/(?P<pr_number>\d+)", TargetStatusView.as_view(), name='target_status')
]
