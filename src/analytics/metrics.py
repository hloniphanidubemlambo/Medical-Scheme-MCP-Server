# Analytics and Metrics Collection

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json
from pathlib import Path

class AnalyticsCollector:
    """
    Collect and analyze healthcare operation metrics.
    Provides insights for population health and operational efficiency.
    """
    
    def __init__(self, storage_path: str = "analytics_data.json"):
        self.storage_path = Path(storage_path)
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """Load existing metrics from storage"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {
            "claims": [],
            "authorizations": [],
            "benefit_checks": [],
            "schemes": defaultdict(lambda: {"total_claims": 0, "total_amount": 0}),
            "procedures": defaultdict(int),
            "daily_stats": defaultdict(lambda: {"claims": 0, "authorizations": 0})
        }
    
    def _save_metrics(self):
        """Persist metrics to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)
    
    def record_claim(
        self,
        scheme_name: str,
        amount: float,
        procedure_codes: List[str],
        status: str,
        patient_id: Optional[str] = None
    ):
        """Record claim submission"""
        claim_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "scheme_name": scheme_name,
            "amount": amount,
            "procedure_codes": procedure_codes,
            "status": status,
            "patient_id": patient_id
        }
        
        self.metrics["claims"].append(claim_record)
        self.metrics["schemes"][scheme_name]["total_claims"] += 1
        self.metrics["schemes"][scheme_name]["total_amount"] += amount
        
        for code in procedure_codes:
            self.metrics["procedures"][code] += 1
        
        date_key = datetime.utcnow().date().isoformat()
        self.metrics["daily_stats"][date_key]["claims"] += 1
        
        self._save_metrics()
    
    def record_authorization(
        self,
        scheme_name: str,
        procedure_code: str,
        status: str,
        amount: Optional[float] = None
    ):
        """Record authorization request"""
        auth_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "scheme_name": scheme_name,
            "procedure_code": procedure_code,
            "status": status,
            "amount": amount
        }
        
        self.metrics["authorizations"].append(auth_record)
        
        date_key = datetime.utcnow().date().isoformat()
        self.metrics["daily_stats"][date_key]["authorizations"] += 1
        
        self._save_metrics()
    
    def get_scheme_statistics(self, scheme_name: Optional[str] = None) -> Dict:
        """Get statistics for specific scheme or all schemes"""
        if scheme_name:
            return self.metrics["schemes"].get(scheme_name, {})
        return dict(self.metrics["schemes"])
    
    def get_top_procedures(self, limit: int = 10) -> List[Dict]:
        """Get most common procedures"""
        sorted_procedures = sorted(
            self.metrics["procedures"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"procedure_code": code, "count": count}
            for code, count in sorted_procedures
        ]
    
    def get_daily_trends(self, days: int = 30) -> Dict:
        """Get daily trends for specified period"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).date()
        
        trends = {
            date: stats
            for date, stats in self.metrics["daily_stats"].items()
            if datetime.fromisoformat(date).date() >= cutoff_date
        }
        
        return trends
    
    def get_approval_rates(self) -> Dict:
        """Calculate approval rates for claims and authorizations"""
        total_claims = len(self.metrics["claims"])
        approved_claims = len([c for c in self.metrics["claims"] if c["status"] == "approved"])
        
        total_auths = len(self.metrics["authorizations"])
        approved_auths = len([a for a in self.metrics["authorizations"] if a["status"] == "approved"])
        
        return {
            "claims": {
                "total": total_claims,
                "approved": approved_claims,
                "approval_rate": (approved_claims / total_claims * 100) if total_claims > 0 else 0
            },
            "authorizations": {
                "total": total_auths,
                "approved": approved_auths,
                "approval_rate": (approved_auths / total_auths * 100) if total_auths > 0 else 0
            }
        }
    
    def get_summary_dashboard(self) -> Dict:
        """Get comprehensive dashboard summary"""
        return {
            "overview": {
                "total_claims": len(self.metrics["claims"]),
                "total_authorizations": len(self.metrics["authorizations"]),
                "total_benefit_checks": len(self.metrics["benefit_checks"]),
                "active_schemes": len(self.metrics["schemes"])
            },
            "scheme_statistics": self.get_scheme_statistics(),
            "top_procedures": self.get_top_procedures(10),
            "approval_rates": self.get_approval_rates(),
            "recent_trends": self.get_daily_trends(7)
        }

# Global analytics instance
analytics = AnalyticsCollector()
