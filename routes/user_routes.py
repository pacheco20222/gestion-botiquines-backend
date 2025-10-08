"""
User authentication and management routes.
Updated to support super_admin and company_admin roles.
"""

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from db import db
from models.models import User, Company

bp = Blueprint("users", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login - FIXED to handle both form and JSON data"""
    if request.method == "GET":
        # Check if already logged in
        if current_user.is_authenticated and getattr(current_user, "active", False):
            return redirect(url_for("pages.dashboard"))
        return render_template("login.html")

    if request.method == "POST":
        # Handle both form data and JSON data
        if request.content_type and 'application/json' in request.content_type:
            data = request.json or {}
        else:
            # Handle form data (from HTML form)
            data = request.form.to_dict()

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            error_msg = "Username and password are required"
            if request.content_type and 'application/json' in request.content_type:
                return jsonify({"error": error_msg}), 400
            else:
                return render_template("login.html", error=error_msg)

        # Query user
        user = User.query.filter_by(username=username, active=True).first()

        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            
            # Redirect based on request type
            if request.content_type and 'application/json' in request.content_type:
                return jsonify({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "user_type": user.user_type,
                        "company": user.company.name if user.company else None
                    }
                }), 200
            else:
                return redirect(url_for("pages.dashboard"))
        else:
            error_msg = "Invalid credentials"
            if request.content_type and 'application/json' in request.content_type:
                return jsonify({"error": error_msg}), 401
            else:
                flash(error_msg, "danger")
                return render_template("login.html", error=error_msg)


@bp.route("/logout")
def logout():
    """Handle user logout"""
    if current_user.is_authenticated:
        logout_user()
        flash("Sesión cerrada correctamente", "success")
    return redirect(url_for("users.login"))


@bp.route("/api/users", methods=["GET"])
def list_users():
    """
    List users. 
    Super admin sees all users, company admin sees only their company users.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401

    if not getattr(current_user, "active", False):
        return jsonify({"error": "User not found"}), 404

    if current_user.is_super_admin():
        # Super admin sees all
        users = User.query.all()
    else:
        # Company admin sees only their company
        users = User.query.filter_by(company_id=current_user.company_id).all()
    
    return jsonify([u.to_dict() for u in users]), 200


@bp.route("/api/users", methods=["POST"])
def create_user():
    """
    Create a new user.
    Only super_admin can create users.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401

    if not current_user.is_super_admin():
        return jsonify({"error": "Only super admin can create users"}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    required = ["username", "password", "user_type"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    
    # Check if username exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400
    
    # Validate user type
    if data["user_type"] not in ["super_admin", "company_admin"]:
        return jsonify({"error": "Invalid user_type. Must be 'super_admin' or 'company_admin'"}), 400
    
    # If company_admin, require company_id
    if data["user_type"] == "company_admin":
        if "company_id" not in data:
            return jsonify({"error": "company_id required for company_admin"}), 400
        
        company = Company.query.get(data["company_id"])
        if not company:
            return jsonify({"error": f"Company {data['company_id']} not found"}), 404
    
    # Create user
    user = User(
        username=data["username"],
        email=data.get("email"),
        user_type=data["user_type"],
        company_id=data.get("company_id") if data["user_type"] == "company_admin" else None,
        active=data.get("active", True)
    )
    user.set_password(data["password"])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


@bp.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user details"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not getattr(current_user, "active", False):
        return jsonify({"error": "Current user not found"}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check permissions
    if not current_user.is_super_admin():
        if user.company_id != current_user.company_id:
            return jsonify({"error": "Access denied"}), 403
    
    return jsonify(user.to_dict()), 200


@bp.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update user.
    Super admin can update anyone, company admin can only update their company users.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not getattr(current_user, "active", False):
        return jsonify({"error": "Current user not found"}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check permissions
    if not current_user.is_super_admin():
        if user.company_id != current_user.company_id:
            return jsonify({"error": "Access denied"}), 403
        # Company admin cannot change user_type or company_id
        data = request.get_json() or {}
        if "user_type" in data or "company_id" in data:
            return jsonify({"error": "Cannot modify user_type or company_id"}), 403
    
    data = request.get_json() or {}
    
    # Update fields
    if "email" in data:
        user.email = data["email"]
    
    if "password" in data and data["password"]:
        user.set_password(data["password"])
    
    if "active" in data:
        user.active = data["active"]
    
    # Only super admin can change these
    if current_user.is_super_admin():
        if "user_type" in data:
            if data["user_type"] not in ["super_admin", "company_admin"]:
                return jsonify({"error": "Invalid user_type"}), 400
            user.user_type = data["user_type"]
        
        if "company_id" in data:
            if data["company_id"]:
                company = Company.query.get(data["company_id"])
                if not company:
                    return jsonify({"error": f"Company {data['company_id']} not found"}), 404
            user.company_id = data["company_id"]
    
    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete (deactivate) user.
    Only super_admin can delete users.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401

    if not current_user.is_super_admin():
        return jsonify({"error": "Only super admin can delete users"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    # Soft delete (deactivate)
    user.active = False
    db.session.commit()
    
    return jsonify({"message": "User deactivated successfully"}), 200


@bp.route("/api/profile", methods=["GET"])
def get_profile():
    """Get current user profile"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401

    if not getattr(current_user, "active", False):
        return jsonify({"error": "User not found"}), 404

    return jsonify(current_user.to_dict()), 200


@bp.route("/api/profile/password", methods=["PUT"])
def change_password():
    """Change current user's password"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = current_user
    if not getattr(user, "active", False):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json() or {}
    
    # Validate fields
    if "current_password" not in data or "new_password" not in data:
        return jsonify({"error": "Current and new password required"}), 400
    
    # Verify current password
    if not user.check_password(data["current_password"]):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Update password
    user.set_password(data["new_password"])
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"}), 200


@bp.route("/api/auth/check", methods=["GET"])
def check_auth():
    """Check if user is authenticated and return session info"""
    if not current_user.is_authenticated or not getattr(current_user, "active", False):
        return jsonify({"authenticated": False}), 200

    user = current_user
    return jsonify({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "user_type": user.user_type,
            "company": user.company.name if user.company else None
        }
    }), 200
