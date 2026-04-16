"""
Customer Reviews & Ratings router.
Customers can rate a service after their appointment is completed.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import List, Optional
import models
from database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    booking_id: int
    customer_name: str
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = ""


class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    service_id: int
    salon_id: int
    customer_name: str
    rating: int
    comment: str

    class Config:
        from_attributes = True


class ServiceRating(BaseModel):
    service_id: int
    service_name: str
    avg_rating: float
    total_reviews: int


@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Submit a review for a completed booking."""
    booking = db.query(models.Booking).filter(models.Booking.id == review.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if review already exists for this booking
    existing = db.query(models.Review).filter(models.Review.booking_id == review.booking_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Review already submitted for this booking")

    db_review = models.Review(
        booking_id=review.booking_id,
        service_id=booking.service_id,
        salon_id=booking.salon_id or 1,
        customer_name=review.customer_name,
        rating=review.rating,
        comment=review.comment or "",
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/{salon_id}", response_model=List[ReviewResponse])
def get_reviews(salon_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a salon."""
    return db.query(models.Review).filter(models.Review.salon_id == salon_id).order_by(models.Review.id.desc()).all()


@router.get("/{salon_id}/ratings", response_model=List[ServiceRating])
def get_service_ratings(salon_id: int, db: Session = Depends(get_db)):
    """Get average ratings per service for a salon."""
    rows = (
        db.query(
            models.Review.service_id,
            func.avg(models.Review.rating).label("avg_rating"),
            func.count(models.Review.id).label("total"),
        )
        .filter(models.Review.salon_id == salon_id)
        .group_by(models.Review.service_id)
        .all()
    )

    results = []
    for service_id, avg_rating, total in rows:
        svc = db.query(models.Service).filter(models.Service.id == service_id).first()
        results.append(ServiceRating(
            service_id=service_id,
            service_name=svc.name if svc else f"Service #{service_id}",
            avg_rating=round(float(avg_rating), 1),
            total_reviews=total,
        ))
    return results


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"message": f"Review {review_id} deleted"}
