"""
ML Model Training API Routes
Provides endpoints for training and using ML models for issue prediction.
"""
from fastapi import APIRouter, HTTPException, Request, Query, BackgroundTasks

from services.ml_model_trainer import ml_issue_predictor

router = APIRouter(prefix="/ml-model", tags=["ML Model Training"])


def is_admin_user(user: dict) -> bool:
    """Check if user has admin access"""
    if not user:
        return False
    return (
        user.get("role") == "admin" or
        user.get("is_admin") or
        "all" in user.get("permissions", [])
    )


@router.get("/info")
async def get_model_info():
    """Get information about the current ML model"""
    return ml_issue_predictor.get_model_info()


@router.post("/train")
async def train_model(
    request: Request,
    days: int = Query(default=30, ge=7, le=90, description="Days of data to use for training"),
    background_tasks: BackgroundTasks = None
):
    """
    Train the ML model on collected data.
    Requires admin access. Training may take a few minutes.
    """
    from routes.auth import get_current_user
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Train synchronously (usually fast enough)
    result = await ml_issue_predictor.train(days=days)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Training failed"))
    
    return result


@router.get("/predict")
async def predict_issues(
    window_minutes: int = Query(default=5, ge=1, le=60, description="Minutes of data to analyze")
):
    """
    Get ML-powered prediction for current system health.
    Returns prediction (healthy/degraded/critical) with confidence score.
    """
    result = await ml_issue_predictor.predict(window_minutes=window_minutes)
    
    if not result.get("success"):
        if "not trained" in result.get("error", "").lower():
            return {
                "prediction": "unknown",
                "confidence": 0,
                "note": "ML model not trained yet. Use rule-based predictor or train the model.",
                "model_trained": False
            }
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result


@router.get("/status")
async def get_training_status():
    """Get ML model training status and metrics"""
    info = ml_issue_predictor.get_model_info()
    
    return {
        "model_ready": info.get("trained", False),
        "version": info.get("version"),
        "metrics": info.get("metrics"),
        "trained_at": info.get("trained_at"),
        "feature_count": len(info.get("feature_columns", [])),
        "classes": info.get("classes", [])
    }


@router.post("/retrain")
async def retrain_model(
    request: Request,
    days: int = Query(default=30, ge=7, le=90)
):
    """Force retrain the model with fresh data"""
    from routes.auth import get_current_user
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Clear existing model
    ml_issue_predictor.is_trained = False
    ml_issue_predictor.rf_model = None
    ml_issue_predictor.gb_model = None
    
    # Retrain
    result = await ml_issue_predictor.train(days=days)
    
    return {
        "retrained": result.get("success", False),
        "result": result
    }


@router.get("/feature-importance")
async def get_feature_importance():
    """Get feature importance from the trained model"""
    if not ml_issue_predictor.is_trained:
        return {
            "available": False,
            "message": "Model not trained yet"
        }
    
    try:
        importance = dict(zip(
            ml_issue_predictor.feature_columns,
            ml_issue_predictor.rf_model.feature_importances_.tolist()
        ))
        
        # Sort by importance
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "available": True,
            "features": [
                {"name": name, "importance": round(imp, 4)}
                for name, imp in sorted_importance
            ]
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }
