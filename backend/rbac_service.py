"""
Role-Based Access Control (RBAC) Service for BookSmart AI
Manages user roles, permissions, and access control
"""
from enum import Enum
from typing import List, Dict, Optional, Set
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    SALON_ADMIN = "salon_admin"
    MANAGER = "manager"
    STAFF = "staff"
    RECEPTIONIST = "receptionist"
    READONLY = "readonly"

class Permission(str, Enum):
    # Booking permissions
    BOOKING_VIEW = "booking:view"
    BOOKING_CREATE = "booking:create"
    BOOKING_UPDATE = "booking:update"
    BOOKING_DELETE = "booking:delete"
    BOOKING_CANCEL = "booking:cancel"
    
    # Customer permissions
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_DELETE = "customer:delete"
    
    # Staff permissions
    STAFF_VIEW = "staff:view"
    STAFF_CREATE = "staff:create"
    STAFF_UPDATE = "staff:update"
    STAFF_DELETE = "staff:delete"
    STAFF_MANAGE_SCHEDULE = "staff:manage_schedule"
    
    # Service permissions
    SERVICE_VIEW = "service:view"
    SERVICE_CREATE = "service:create"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    
    # Financial permissions
    FINANCE_VIEW = "finance:view"
    FINANCE_MANAGE = "finance:manage"
    PAYMENT_PROCESS = "payment:process"
    REFUND_PROCESS = "refund:process"
    
    # Report permissions
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    ANALYTICS_VIEW = "analytics:view"
    
    # Settings permissions
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"
    SALON_SETTINGS = "salon:settings"
    
    # System permissions
    AUDIT_VIEW = "audit:view"
    USER_MANAGE = "user:manage"
    ROLE_ASSIGN = "role:assign"
    DATA_EXPORT = "data:export"
    
    # Marketing permissions
    MARKETING_SEND = "marketing:send"
    PROMOTION_CREATE = "promotion:create"
    
    # Communication permissions
    SMS_SEND = "sms:send"
    EMAIL_SEND = "email:send"
    WHATSAPP_SEND = "whatsapp:send"

class RolePermissions:
    """Define permissions for each role"""
    
    ROLE_PERMISSIONS = {
        Role.SUPER_ADMIN: set(Permission),  # All permissions
        
        Role.SALON_ADMIN: {
            Permission.BOOKING_VIEW, Permission.BOOKING_CREATE, 
            Permission.BOOKING_UPDATE, Permission.BOOKING_DELETE, Permission.BOOKING_CANCEL,
            Permission.CUSTOMER_VIEW, Permission.CUSTOMER_CREATE, 
            Permission.CUSTOMER_UPDATE, Permission.CUSTOMER_DELETE,
            Permission.STAFF_VIEW, Permission.STAFF_CREATE, 
            Permission.STAFF_UPDATE, Permission.STAFF_DELETE, Permission.STAFF_MANAGE_SCHEDULE,
            Permission.SERVICE_VIEW, Permission.SERVICE_CREATE, 
            Permission.SERVICE_UPDATE, Permission.SERVICE_DELETE,
            Permission.FINANCE_VIEW, Permission.FINANCE_MANAGE, 
            Permission.PAYMENT_PROCESS, Permission.REFUND_PROCESS,
            Permission.REPORT_VIEW, Permission.REPORT_EXPORT, Permission.ANALYTICS_VIEW,
            Permission.SETTINGS_VIEW, Permission.SETTINGS_UPDATE, Permission.SALON_SETTINGS,
            Permission.AUDIT_VIEW, Permission.USER_MANAGE, Permission.ROLE_ASSIGN,
            Permission.DATA_EXPORT, Permission.MARKETING_SEND, Permission.PROMOTION_CREATE,
            Permission.SMS_SEND, Permission.EMAIL_SEND, Permission.WHATSAPP_SEND
        },
        
        Role.MANAGER: {
            Permission.BOOKING_VIEW, Permission.BOOKING_CREATE, 
            Permission.BOOKING_UPDATE, Permission.BOOKING_CANCEL,
            Permission.CUSTOMER_VIEW, Permission.CUSTOMER_CREATE, Permission.CUSTOMER_UPDATE,
            Permission.STAFF_VIEW, Permission.STAFF_UPDATE, Permission.STAFF_MANAGE_SCHEDULE,
            Permission.SERVICE_VIEW,
            Permission.FINANCE_VIEW,
            Permission.REPORT_VIEW, Permission.ANALYTICS_VIEW,
            Permission.SETTINGS_VIEW,
            Permission.SMS_SEND, Permission.EMAIL_SEND, Permission.WHATSAPP_SEND
        },
        
        Role.STAFF: {
            Permission.BOOKING_VIEW, Permission.BOOKING_CREATE, Permission.BOOKING_UPDATE,
            Permission.CUSTOMER_VIEW, Permission.CUSTOMER_CREATE,
            Permission.STAFF_VIEW,
            Permission.SERVICE_VIEW,
            Permission.SMS_SEND, Permission.EMAIL_SEND
        },
        
        Role.RECEPTIONIST: {
            Permission.BOOKING_VIEW, Permission.BOOKING_CREATE, 
            Permission.BOOKING_UPDATE, Permission.BOOKING_CANCEL,
            Permission.CUSTOMER_VIEW, Permission.CUSTOMER_CREATE, Permission.CUSTOMER_UPDATE,
            Permission.STAFF_VIEW,
            Permission.SERVICE_VIEW,
            Permission.SMS_SEND, Permission.WHATSAPP_SEND
        },
        
        Role.READONLY: {
            Permission.BOOKING_VIEW,
            Permission.CUSTOMER_VIEW,
            Permission.STAFF_VIEW,
            Permission.SERVICE_VIEW,
            Permission.REPORT_VIEW,
            Permission.ANALYTICS_VIEW
        }
    }

class UserRole(BaseModel):
    user_id: str
    email: str
    role: Role
    salon_id: str
    assigned_by: str
    assigned_at: str
    is_active: bool = True

class RBACService:
    """Role-Based Access Control Service"""
    
    def __init__(self):
        self.user_roles: Dict[str, UserRole] = {}  # user_id -> UserRole
        self.role_permissions = RolePermissions.ROLE_PERMISSIONS
    
    def assign_role(self, user_id: str, email: str, role: Role, 
                   salon_id: str, assigned_by: str) -> UserRole:
        """Assign role to user"""
        
        user_role = UserRole(
            user_id=user_id,
            email=email,
            role=role,
            salon_id=salon_id,
            assigned_by=assigned_by,
            assigned_at=__import__('datetime').datetime.now().isoformat()
        )
        
        self.user_roles[user_id] = user_role
        
        logger.info(f"[RBAC] Assigned {role} to {email} in salon {salon_id}")
        
        return user_role
    
    def change_role(self, user_id: str, new_role: Role, changed_by: str) -> bool:
        """Change user's role"""
        if user_id not in self.user_roles:
            return False
        
        old_role = self.user_roles[user_id].role
        self.user_roles[user_id].role = new_role
        self.user_roles[user_id].assigned_by = changed_by
        self.user_roles[user_id].assigned_at = __import__('datetime').datetime.now().isoformat()
        
        logger.info(f"[RBAC] Changed role for {user_id}: {old_role} → {new_role}")
        
        return True
    
    def revoke_role(self, user_id: str) -> bool:
        """Revoke user's role"""
        if user_id not in self.user_roles:
            return False
        
        del self.user_roles[user_id]
        logger.info(f"[RBAC] Revoked role for {user_id}")
        
        return True
    
    def get_user_role(self, user_id: str) -> Optional[UserRole]:
        """Get user's role"""
        return self.user_roles.get(user_id)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user_role = self.get_user_role(user_id)
        
        if not user_role or not user_role.is_active:
            return False
        
        permissions = self.role_permissions.get(user_role.role, set())
        return permission in permissions
    
    def check_permissions(self, user_id: str, permissions: List[Permission]) -> Dict[str, bool]:
        """Check multiple permissions for user"""
        return {p.value: self.has_permission(user_id, p) for p in permissions}
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for user"""
        user_role = self.get_user_role(user_id)
        
        if not user_role:
            return []
        
        permissions = self.role_permissions.get(user_role.role, set())
        return [p.value for p in permissions]
    
    def require_permission(self, user_id: str, permission: Permission):
        """Decorator/requirement checker for permissions"""
        if not self.has_permission(user_id, permission):
            raise PermissionError(f"User does not have permission: {permission}")
        return True
    
    def get_salon_users(self, salon_id: str, role: Role = None) -> List[Dict]:
        """Get all users for a salon"""
        users = []
        
        for user_role in self.user_roles.values():
            if user_role.salon_id != salon_id:
                continue
            if role and user_role.role != role:
                continue
            
            users.append({
                "user_id": user_role.user_id,
                "email": user_role.email,
                "role": user_role.role,
                "is_active": user_role.is_active,
                "assigned_at": user_role.assigned_at
            })
        
        return users
    
    def get_role_stats(self, salon_id: str = None) -> Dict:
        """Get role distribution statistics"""
        role_counts = {}
        
        for user_role in self.user_roles.values():
            if salon_id and user_role.salon_id != salon_id:
                continue
            
            role = user_role.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_users": len(self.user_roles),
            "role_distribution": role_counts,
            "active_users": sum(1 for u in self.user_roles.values() if u.is_active)
        }
    
    def can_access_resource(self, user_id: str, resource_salon_id: str) -> bool:
        """Check if user can access resources from a specific salon"""
        user_role = self.get_user_role(user_id)
        
        if not user_role:
            return False
        
        # Super admin can access all salons
        if user_role.role == Role.SUPER_ADMIN:
            return True
        
        # Users can only access their own salon
        return user_role.salon_id == resource_salon_id

# Initialize RBAC service
rbac_service = RBACService()

# Convenience functions
async def assign_user_role(user_id: str, email: str, role: Role, salon_id: str, assigned_by: str):
    """Assign role to user"""
    return rbac_service.assign_role(user_id, email, role, salon_id, assigned_by)

async def check_user_permission(user_id: str, permission: Permission):
    """Check if user has permission"""
    return rbac_service.has_permission(user_id, permission)

async def get_user_role_info(user_id: str):
    """Get user's role information"""
    role = rbac_service.get_user_role(user_id)
    if role:
        return {
            "role": role.role,
            "salon_id": role.salon_id,
            "permissions": rbac_service.get_user_permissions(user_id)
        }
    return None

async def require_permission_check(user_id: str, permission: Permission):
    """Require permission check (raises exception if not allowed)"""
    return rbac_service.require_permission(user_id, permission)
