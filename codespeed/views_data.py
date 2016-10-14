# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

from codespeed.models import Executable, Revision, Project, Branch


def get_default_environment(enviros, data, multi=False):
    """Returns the default environment. Preference level is:
        * Present in URL parameters (permalinks)
        * Value in settings.py
        * First Environment ID

    """
    defaultenviros = []
    # Use permalink values
    if 'env' in data:
        for env_value in data['env'].split(","):
            for env in enviros:
                try:
                    env_id = int(env_value)
                except ValueError:
                    # Not an int
                    continue
                for env in enviros:
                    if env_id == env.id:
                        defaultenviros.append(env)
            if not multi:
                break
    # Use settings.py value
    if not defaultenviros and not multi:
        if (hasattr(settings, 'DEF_ENVIRONMENT') and
                settings.DEF_ENVIRONMENT is not None):
            for env in enviros:
                if settings.DEF_ENVIRONMENT == env.name:
                    defaultenviros.append(env)
                    break
    # Last fallback
    if not defaultenviros:
        defaultenviros = enviros
    if multi:
        return defaultenviros
    else:
        return defaultenviros[0]


def getbaselineexecutables():
    baseline = [{
        'key': "none",
        'name': "None",
        'executable': "none",
        'revision': "none",
    }]
    executables = Executable.objects.select_related('project')
    revs = Revision.objects.exclude(tag="").select_related('branch__project')
    if not revs.exists():
        revs = Revision.objects.filter(branch__name='default').select_related('branch__project')
    maxlen = 22
    for rev in revs:
        # Add executables that correspond to each tagged revision.
        for exe in [e for e in executables if e.project == rev.branch.project]:
            exestring = str(exe)
            if len(exestring) > maxlen:
                exestring = str(exe)[0:maxlen] + "..."
            name = exestring + " " + rev.tag
            key = str(exe.id) + "+" + str(rev.id)
            baseline.append({
                'key': key,
                'executable': exe,
                'revision': rev,
                'name': name,
            })
    # move default to first place
    if hasattr(settings, 'DEF_BASELINE') and settings.DEF_BASELINE is not None:
        try:
            exename = settings.DEF_BASELINE['executable']
            commitid = settings.DEF_BASELINE['revision']
            for base in baseline:
                if base['key'] == "none":
                    continue
                if (base['executable'].name == exename and
                        base['revision'].commitid == commitid):
                    baseline.remove(base)
                    baseline.insert(1, base)
                    break
        except KeyError:
            # TODO: write to server logs
            # error in settings.DEF_BASELINE
            pass
    return baseline


def getdefaultexecutable():
    default = None
    if (hasattr(settings, 'DEF_EXECUTABLE') and
            settings.DEF_EXECUTABLE is not None):
        try:
            default = Executable.objects.get(name=settings.DEF_EXECUTABLE)
        except Executable.DoesNotExist:
            pass
    if default is None:
        execquery = Executable.objects.filter(project__track=True)
        if len(execquery):
            default = execquery[0]

    return default


def getcomparisonexes():
    all_executables = {}
    exekeys = []
    baselines = getbaselineexecutables()
    for proj in Project.objects.all():
        executables = []
        executablekeys = []
        maxlen = 20
        # add all tagged revs for any project
        for exe in baselines:
            if exe['key'] is not "none" and exe['executable'].project == proj:
                executablekeys.append(exe['key'])
                executables.append(exe)

        # add latest revs of the project
        branches = Branch.objects.filter(project=proj)
        for branch in branches:
            try:
                rev = Revision.objects.filter(branch=branch).latest('date')
            except Revision.DoesNotExist:
                continue
            # Now only append when tag == "",
            # because we already added tagged revisions
            if rev.tag == "":
                for exe in Executable.objects.filter(project=proj):
                    exestring = str(exe)
                    if len(exestring) > maxlen:
                        exestring = str(exe)[0:maxlen] + "..."
                    name = exestring + " latest"
                    if branch.name != 'default':
                        name += " in branch '" + branch.name + "'"
                    key = str(exe.id) + "+L+" + branch.name
                    executablekeys.append(key)
                    executables.append({
                        'key': key,
                        'executable': exe,
                        'revision': rev,
                        'name': name,
                    })
        all_executables[proj] = executables
        exekeys += executablekeys
    return all_executables, exekeys
