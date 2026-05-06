from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from models.models import Botiquin, Company, Medicine

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Basic Authentication Check
        if not current_user.is_authenticated or not getattr(current_user, "active", False):
            return jsonify({"error": "Not authenticated"}), 401
        
        # Super admin has bypass for isolation checks
        if current_user.is_super_admin():
            return f(*args, **kwargs)
        
        # 2. Company Isolation Check (URL parameters)
        # Check company_id in route parameters
        if 'company_id' in kwargs:
            try:
                if int(kwargs['company_id']) != current_user.company_id:
                    return jsonify({"error": "Access denied: cannot access another company's data"}), 403
            except (ValueError, TypeError):
                pass
                
        # Check botiquin_id in route parameters
        if 'botiquin_id' in kwargs:
            try:
                bot = Botiquin.query.get(int(kwargs['botiquin_id']))
                if bot and bot.company_id != current_user.company_id:
                    return jsonify({"error": "Access denied: botiquin belongs to another company"}), 403
            except (ValueError, TypeError):
                pass
        
        # Check med_id in route parameters
        if 'med_id' in kwargs:
            try:
                med = Medicine.query.get(int(kwargs['med_id']))
                if med and med.botiquin.company_id != current_user.company_id:
                    return jsonify({"error": "Access denied: medicine belongs to another company"}), 403
            except (ValueError, TypeError):
                pass

        # 3. Company Isolation Check (Query parameters)
        q_company_id = request.args.get('company_id')
        if q_company_id:
            try:
                if int(q_company_id) != current_user.company_id:
                    return jsonify({"error": "Access denied: cannot filter by another company"}), 403
            except (ValueError, TypeError):
                pass
        
        q_botiquin_id = request.args.get('botiquin_id')
        if q_botiquin_id:
            try:
                bot = Botiquin.query.get(int(q_botiquin_id))
                if bot and bot.company_id != current_user.company_id:
                    return jsonify({"error": "Access denied: cannot filter by another company's botiquin"}), 403
            except (ValueError, TypeError):
                pass

        return f(*args, **kwargs)
    return decorated_function
