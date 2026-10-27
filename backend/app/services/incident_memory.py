import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.db_models import IncidentModel, IncidentEvidenceModel, VerifiedFeedbackModel
from app.models.schemas import IncidentSchema

class IncidentMemoryService:
    @staticmethod
    def get_similar_incidents(category: str, root_cause: str, db: Session, limit: int = 3) -> List[Dict[str, Any]]:
        """Transparent similarity retrieval based on category matching and verified outcomes."""
        query = db.query(IncidentModel).filter(
            (IncidentModel.category == category) | (IncidentModel.status == "confirmed")
        ).order_by(IncidentModel.created_at.desc()).limit(limit)

        results = []
        for inc in query.all():
            feedbacks = db.query(VerifiedFeedbackModel).filter(VerifiedFeedbackModel.incident_id == inc.id).all()
            results.append({
                "incident_id": inc.id,
                "title": inc.title,
                "category": inc.category,
                "suspected_root_cause": inc.suspected_root_cause,
                "status": inc.status,
                "confidence_score": inc.confidence_score,
                "created_at": inc.created_at.isoformat(),
                "verified_feedback": [
                    {
                        "confirmed_root_cause": fb.confirmed_root_cause,
                        "recovery_taken": fb.actual_recovery_taken,
                        "notes": fb.feedback_notes
                    } for fb in feedbacks
                ]
            })
        return results

incident_memory = IncidentMemoryService()
