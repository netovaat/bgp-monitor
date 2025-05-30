"""
Monitoring Routes - System monitoring endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import psutil
import time
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "BGP Monitor v2.0"
    }

@router.get("/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting metrics: {str(e)}")

@router.get("/status")
async def get_service_status():
    """Get BGP monitoring service status"""
    return {
        "bgp_monitor": {
            "status": "running",
            "version": "2.0",
            "uptime": "running",
            "last_collection": datetime.utcnow().isoformat()
        },
        "database": {
            "status": "connected",
            "type": "postgresql"
        },
        "scheduler": {
            "status": "active",
            "next_run": (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        }
    }

@router.get("/alerts")
async def get_recent_alerts(limit: int = 10):
    """Get recent system alerts"""
    # This would typically query the database for recent alerts
    return {
        "total_alerts": 0,
        "alerts": [],
        "last_check": datetime.utcnow().isoformat()
    }
