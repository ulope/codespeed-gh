import json
from logging import getLogger

from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView

from github_integration.models import Target
from github_integration.runner import run_jobs
from github_integration.utils import get_target_commit

log = getLogger(__name__)


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        event = request.META.get('HTTP_X_GITHUB_EVENT')
        event_data = json.loads(request.body.decode("UTF-8"))
        print("="*80)
        if (event == 'pull_request' and event_data['action'] in {'opened', 'synchronize'}) or event == 'push':
            target, commit = get_target_commit(event_data)
            log.info("Enqueing job for %s", commit)
            run_jobs.delay(commit.id)
    return HttpResponse(status=201)


class TargetStatusView(DetailView):
    model = Target

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.filter(
            repo_name=self.kwargs.get('repo_name'),
            pr_number=self.kwargs.get('pr_number')
        )
        try:
            return queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
