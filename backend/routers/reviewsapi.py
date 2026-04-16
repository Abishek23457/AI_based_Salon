"""
Reviews API Router for BookSmart AI
API endpoints for customer reviews and ratings
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from review_system import review_system, submit_customer_review, get_service_reviews, get_service_rating_summary

router = APIRouter(prefix="/reviewsapi", tags=["Reviews"])

class SubmitReviewRequest(BaseModel):
    booking_id: str
    customer_id: str
    customer_name: str
    service_id: str
    service_name: str
    staff_id: str
    staff_name: str
    rating: int
    title: str
    comment: str
    service_quality: Optional[int] = None
    staff_professionalism: Optional[int] = None
    value_for_money: Optional[int] = None
    ambience: Optional[int] = None

class ModerateReviewRequest(BaseModel):
    action: str  # approve, reject, archive
    admin_response: Optional[str] = None

class VoteRequest(BaseModel):
    customer_id: str
    vote_type: str  # helpful, unhelpful

@router.post("/submit")
async def submit_review(request: SubmitReviewRequest):
    """Submit a new review"""
    try:
        review = await submit_customer_review(**request.model_dump())
        return {
            "success": True,
            "review_id": review.id,
            "status": review.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/service/{service_id}")
async def get_service_reviews_api(
    service_id: str,
    status: str = "published",
    min_rating: Optional[int] = None,
    sort_by: str = "newest"
):
    """Get reviews for a service"""
    reviews = await get_service_reviews(
        service_id,
        status=status,
        min_rating=min_rating,
        sort_by=sort_by
    )
    return {"reviews": reviews}

@router.get("/service/{service_id}/rating")
async def get_service_rating(service_id: str):
    """Get aggregated rating for a service"""
    rating = await get_service_rating_summary(service_id)
    return rating

@router.get("/staff/{staff_id}")
async def get_staff_reviews(
    staff_id: str,
    status: str = "published"
):
    """Get reviews for a staff member"""
    reviews = review_system.get_reviews(staff_id=staff_id, status=status)
    return {"reviews": reviews}

@router.get("/pending")
async def get_pending_reviews():
    """Get reviews pending moderation (admin only)"""
    reviews = review_system.get_pending_reviews()
    return {"pending_reviews": reviews}

@router.post("/{review_id}/moderate")
async def moderate_review(review_id: str, request: ModerateReviewRequest):
    """Moderate a review (admin only)"""
    success = review_system.moderate_review(
        review_id,
        request.action,
        request.admin_response
    )
    if success:
        return {"success": True, "message": f"Review {request.action}d"}
    raise HTTPException(status_code=404, detail="Review not found")

@router.post("/{review_id}/vote")
async def vote_review(review_id: str, request: VoteRequest):
    """Vote review as helpful or unhelpful"""
    success = review_system.vote_review(review_id, request.customer_id, request.vote_type)
    if success:
        return {"success": True}
    raise HTTPException(status_code=400, detail="Failed to vote")

@router.get("/stats")
async def get_stats():
    """Get review system statistics"""
    return review_system.get_stats()

@router.get("/customer/{customer_id}")
async def get_customer_reviews(customer_id: str):
    """Get reviews by a customer"""
    reviews = review_system.get_reviews(customer_id=customer_id)
    return {"reviews": reviews}
