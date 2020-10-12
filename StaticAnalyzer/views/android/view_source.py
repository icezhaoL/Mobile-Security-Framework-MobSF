# -*- coding: utf_8 -*-
"""View Source of a file."""

import logging
import ntpath
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.utils.html import escape

from MobSF.forms import FormUtil
from MobSF.utils import (
    is_safe_path,
    print_n_send_error_response)

from StaticAnalyzer.views.shared_func import find_java_source_folder
from StaticAnalyzer.forms import (ViewSourceAndroidApiForm,
                                  ViewSourceAndroidForm)

logger = logging.getLogger(__name__)


def run(request, api=False):
    """View the source of a file."""
    try:
        logger.info('View Android Source File')
        exp = 'Error Description'
        if api:
            fil = request.POST['file']
            md5 = request.POST['hash']
            typ = request.POST['type']
            viewsource_form = ViewSourceAndroidApiForm(request.POST)
        else:
            fil = request.GET['file']
            md5 = request.GET['md5']
            typ = request.GET['type']
            viewsource_form = ViewSourceAndroidForm(request.GET)
        if not viewsource_form.is_valid():
            err = FormUtil.errors_message(viewsource_form)
            return print_n_send_error_response(request, err, api, exp)

        base = Path(settings.UPLD_DIR) / md5
        if typ == 'smali':
            src = base / '/smali_source/'
            syntax = 'smali'
        else:
            try:
                src, syntax, _ = find_java_source_folder(base)
            except StopIteration:
                return print_n_send_error_response(request, 'Invalid Directory Structure', api)

        sfile = src / fil
        if not is_safe_path(src, sfile.as_posix()):
            return print_n_send_error_response(request, 'Path Traversal Detected!', api)
        context = {
            'title': escape(ntpath.basename(fil)),
            'file': escape(ntpath.basename(fil)),
            'dat': sfile.read_text('utf-8', 'ignore'),
            'type': syntax,
            'sql': {},
            'version': settings.MOBSF_VER,
        }
        template = 'general/view.html'
        if api:
            return context
        return render(request, template, context)
    except Exception as exp:
        logger.exception('Error Viewing Source')
        msg = str(exp)
        exp = exp.__doc__
        return print_n_send_error_response(request, msg, api, exp)
