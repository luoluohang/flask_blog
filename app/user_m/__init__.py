from flask import Blueprint
from ..models import Permission

user_m = Blueprint('user_m',__name__)

from . import views

@user_m.app_context_processor
def inject_permissions():
	return dict(Permission = Permission)
