"""
Audit Logging System for BookSmart AI
Tracks all system activities for compliance and security
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AuditAction(str, Enum):
    # Booking actions
    BOOKING_CREATED = "booking_created"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_COMPLETED = "booking_completed"
    
    # Customer actions
    CUSTOMER_CREATED = "customer_created"
    CUSTOMER_UPDATED = "customer_updated"
    CUSTOMER_DELETED = "customer_deleted"
    
    # Staff actions
    STAFF_CREATED = "staff_created"
    STAFF_UPDATED = "staff_updated"
    STAFF_DELETED = "staff_deleted"
    
    # Service actions
    SERVICE_CREATED = "service_created"
    SERVICE_UPDATED = "service_updated"
    SERVICE_DELETED = "service_deleted"
    
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_PASSWORD_CHANGED = "user_password_changed"
    USER_ROLE_CHANGED = "user_role_changed"
    
    # System actions
    SETTINGS_UPDATED = "settings_updated"
    BACKUP_CREATED = "backup_created"
    DATA_EXPORTED = "data_exported"

class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLog(BaseModel):
    id: str
    timestamp: datetime
    action: str
    severity: str
    
    # Actor info
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Target info
    target_type: str  # e.g., "booking", "customer", "staff"
    target_id: str
    target_name: Optional[str] = None
    
    # Change details
    previous_values: Optional[Dict] = None
    new_values: Optional[Dict] = None
    change_summary: str
    
    # Additional context
    salon_id: str
    notes: str = ""
    success: bool = True
    error_message: str = ""

class AuditLogger:
    """Audit Logging Service"""
    
    MAX_LOGS_IN_MEMORY = 10000
    
    def __init__(self):
        self.logs: List[AuditLog] = []
        self.action_severity = {
            AuditAction.BOOKING_CREATED: AuditSeverity.LOW,
            AuditAction.BOOKING_UPDATED: AuditSeverity.MEDIUM,
            AuditAction.BOOKING_CANCELLED: AuditSeverity.MEDIUM,
            AuditAction.BOOKING_COMPLETED: AuditSeverity.LOW,
            AuditAction.CUSTOMER_CREATED: AuditSeverity.LOW,
            AuditAction.CUSTOMER_UPDATED: AuditSeverity.MEDIUM,
            AuditAction.CUSTOMER_DELETED: AuditSeverity.HIGH,
            AuditAction.STAFF_CREATED: AuditSeverity.LOW,
            AuditAction.STAFF_UPDATED: AuditSeverity.MEDIUM,
            AuditAction.STAFF_DELETED: AuditSeverity.HIGH,
            AuditAction.SERVICE_CREATED: AuditSeverity.LOW,
            AuditAction.SERVICE_UPDATED: AuditSeverity.MEDIUM,
            AuditAction.SERVICE_DELETED: AuditSeverity.MEDIUM,
            AuditAction.USER_LOGIN: AuditSeverity.LOW,
            AuditAction.USER_LOGOUT: AuditSeverity.LOW,
            AuditAction.USER_PASSWORD_CHANGED: AuditSeverity.HIGH,
            AuditAction.USER_ROLE_CHANGED: AuditSeverity.CRITICAL,
            AuditAction.SETTINGS_UPDATED: AuditSeverity.HIGH,
            AuditAction.BACKUP_CREATED: AuditSeverity.MEDIUM,
            AuditAction.DATA_EXPORTED: AuditSeverity.CRITICAL
        }
    
    def log(self,
           action: AuditAction,
           target_type: str,
           target_id: str,
           salon_id: str,
           user_id: str = None,
           user_email: str = None,
           user_role: str = None,
           ip_address: str = None,
           user_agent: str = None,
           target_name: str = None,
           previous_values: Dict = None,
           new_values: Dict = None,
           change_summary: str = "",
           notes: str = "",
           success: bool = True,
           error_message: str = "") -> AuditLog:
        """Create audit log entry"""
        
        # Determine severity
        severity = self.action_severity.get(action, AuditSeverity.LOW)
        
        # Generate change summary if not provided
        if not change_summary and previous_values and new_values:
            changes = []
            for key in new_values:
                if key in previous_values and previous_values[key] != new_values[key]:
                    changes.append(f"{key}: {previous_values[key]} → {new_values[key]}")
            change_summary = ", ".join(changes) if changes else "No changes detected"
        
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            previous_values=previous_values,
            new_values=new_values,
            change_summary=change_summary,
            salon_id=salon_id,
            notes=notes,
            success=success,
            error_message=error_message
        )
        
        self.logs.append(log_entry)
        
        # Maintain max size
        if len(self.logs) > self.MAX_LOGS_IN_MEMORY:
            self.logs = self.logs[-self.MAX_LOGS_IN_MEMORY:]
        
        # Log to system logger
        logger.info(f"[Audit] {action} by {user_email} on {target_type}:{target_id}")
        
        return log_entry
    
    def query_logs(self,
                  salon_id: str = None,
                  user_id: str = None,
                  action: str = None,
                  target_type: str = None,
                  target_id: str = None,
                  severity: str = None,
                  start_date: datetime = None,
                  end_date: datetime = None,
                  limit: int = 100) -> List[Dict]:
        """Query audit logs with filters"""
        results = []
        
        for log in reversed(self.logs):  # Most recent first
            if salon_id and log.salon_id != salon_id:
                continue
            if user_id and log.user_id != user_id:
                continue
            if action and log.action != action:
                continue
            if target_type and log.target_type != target_type:
                continue
            if target_id and log.target_id != target_id:
                continue
            if severity and log.severity != severity:
                continue
            if start_date and log.timestamp < start_date:
                continue
            if end_date and log.timestamp > end_date:
                continue
            
            results.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "severity": log.severity,
                "user_email": log.user_email,
                "user_role": log.user_role,
                "ip_address": log.ip_address,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "target_name": log.target_name,
                "change_summary": log.change_summary,
                "success": log.success,
                "notes": log.notes
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get activity history for a specific user"""
        return self.query_logs(user_id=user_id, limit=limit)
    
    def get_object_history(self, target_type: str, target_id: str) -> List[Dict]:
        """Get audit history for a specific object"""
        return self.query_logs(target_type=target_type, target_id=target_id, limit=100)
    
    def get_security_events(self, salon_id: str = None, limit: int = 50) -> List[Dict]:
        """Get high/critical severity security events"""
        high_severity_logs = []
        
        for log in reversed(self.logs):
            if salon_id and log.salon_id != salon_id:
                continue
            if log.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                high_severity_logs.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "severity": log.severity,
                    "user_email": log.user_email,
                    "change_summary": log.change_summary,
                    "target_type": log.target_type,
                    "target_name": log.target_name
                })
                
                if len(high_severity_logs) >= limit:
                    break
        
        return high_severity_logs
    
    def get_stats(self, salon_id: str = None) -> Dict:
        """Get audit statistics"""
        total_logs = 0
        action_counts = {}
        severity_counts = {}
        user_activity = {}
        
        for log in self.logs:
            if salon_id and log.salon_id != salon_id:
                continue
            
            total_logs += 1
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            severity_counts[log.severity] = severity_counts.get(log.severity, 0) + 1
            
            if log.user_email:
                user_activity[log.user_email] = user_activity.get(log.user_email, 0) + 1
        
        # Last 24 hours activity
        last_24h = datetime.now() - __import__('datetime').timedelta(hours=24)
        recent_logs = sum(1 for log in self.logs 
                         if (not salon_id or log.salon_id == salon_id) 
                         and log.timestamp >= last_24h)
        
        return {
            "total_logs": total_logs,
            "last_24h_activity": recent_logs,
            "action_breakdown": action_counts,
            "severity_breakdown": severity_counts,
            "most_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def export_logs(self, format: str = "json", salon_id: str = None) -> str:
        """Export logs for compliance/backup"""
        import json
        
        logs = self.query_logs(salon_id=salon_id, limit=10000)
        
        if format == "json":
            return json.dumps(logs, indent=2)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            return output.getvalue()
        
        return ""

# Initialize audit logger
audit_logger = AuditLogger()

# Convenience functions for common operations
async def log_booking_created(booking_id: str, customer_name: str, salon_id: str, **kwargs):
    """Log booking creation"""
    return audit_logger.log(
        action=AuditAction.BOOKING_CREATED,
        target_type="booking",
        target_id=booking_id,
        target_name=customer_name,
        salon_id=salon_id,
        change_summary=f"Booking created for {customer_name}",
        **kwargs
    )

async def log_booking_updated(booking_id: str, previous: Dict, new: Dict, salon_id: str, **kwargs):
    """Log booking update"""
    return audit_logger.log(
        action=AuditAction.BOOKING_UPDATED,
        target_type="booking",
        target_id=booking_id,
        salon_id=salon_id,
        previous_values=previous,
        new_values=new,
        **kwargs
    )

async def log_user_login(user_id: str, user_email: str, ip_address: str, salon_id: str, **kwargs):
    """Log user login"""
    return audit_logger.log(
        action=AuditAction.USER_LOGIN,
        target_type="user",
        target_id=user_id,
        target_name=user_email,
        salon_id=salon_id,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        change_summary=f"User {user_email} logged in from {ip_address}",
        **kwargs
    )

async def log_data_export(user_id: str, user_email: str, data_type: str, salon_id: str, **kwargs):
    """Log data export (security sensitive)"""
    return audit_logger.log(
        action=AuditAction.DATA_EXPORTED,
        target_type="data_export",
        target_id=str(uuid.uuid4()),
        salon_id=salon_id,
        user_id=user_id,
        user_email=user_email,
        change_summary=f"Exported {data_type} data",
        **kwargs
    )

async def get_audit_trail(salon_id: str = None, limit: int = 100):
    """Get recent audit trail"""
    return audit_logger.query_logs(salon_id=salon_id, limit=limit)

async def get_audit_statistics(salon_id: str = None):
    """Get audit statistics"""
    return audit_logger.get_stats(salon_id)
