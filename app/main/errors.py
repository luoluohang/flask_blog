from flask import render_template,request,jsonify
from . import main
from ..api_1_0 import errors

@main.app_errorhandler(403)
def forbidden(e):
	if request.accept_mimetypes.accept_json and \
		not request.accept_mimetypes.accept_html:
		errors.forbidden("forbidden")
	return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
	if request.accept_mimetypes.accept_json and \
		not request.accept_mimetypes.accept_html:
		errors.bad_request("not found page")
	return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
	if request.accept_mimetypes.accept_json and \
		not request.accept_mimetypes.accept_html:
		response = jsonify({'error': 'internal server error'})
		response.status_code = 500
		return response
	return render_template('500.html'), 500
