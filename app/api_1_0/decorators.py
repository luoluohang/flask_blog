from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def wrappers(*args, **kwargs):
			if not g.current_user.can(permission):
				return forbidden('no permissions')
			return f(*args, **kwargs)
		return wrappers
	return decorator