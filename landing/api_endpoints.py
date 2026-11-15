"""Additional API endpoints for Dashboard, History, and Stats."""
from fastapi import APIRouter, HTTPException
from utils.database_helpers import get_historical_screenings, get_results_for_jd

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/history")
async def get_history(limit: int = 20):
    """Get screening history with aggregate stats."""
    try:
        history = get_historical_screenings(limit=limit)
        return {
            "success": True,
            "count": len(history),
            "screenings": [
                {
                    "jd_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "candidate_count": row[3] or 0,
                    "avg_score": round(row[4], 1) if row[4] else 0
                }
                for row in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.get("/results/{jd_id}")
async def get_results_by_jd(jd_id: int):
    """Get detailed results for a specific job description."""
    try:
        results = get_results_for_jd(jd_id)
        if not results:
            raise HTTPException(status_code=404, detail=f"No results found for JD ID {jd_id}")
        return {
            "success": True,
            "jd_id": jd_id,
            "count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")

@router.get("/stats")
async def get_dashboard_stats():
    """Get aggregate statistics for dashboard."""
    try:
        from database.db import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # Total screenings
        cursor.execute("SELECT COUNT(*) FROM job_descriptions")
        total_screenings = cursor.fetchone()[0]

        # Total candidates
        cursor.execute("SELECT COUNT(DISTINCT candidate_id) FROM screening_results")
        total_candidates = cursor.fetchone()[0]

        # Average score
        cursor.execute("SELECT AVG(score) FROM screening_results")
        avg_score = cursor.fetchone()[0] or 0

        # Best score
        cursor.execute("SELECT MAX(score) FROM screening_results")
        best_score = cursor.fetchone()[0] or 0

        # Top tier distribution
        cursor.execute("""
            SELECT tier, COUNT(*) as count
            FROM screening_results
            GROUP BY tier
        """)
        tier_distribution = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "success": True,
            "stats": {
                "total_screenings": total_screenings,
                "total_candidates": total_candidates,
                "avg_score": round(avg_score, 1),
                "best_score": round(best_score, 1),
                "tier_distribution": tier_distribution
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
