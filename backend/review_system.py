"""
Review System for BookSmart AI
Manages customer reviews and ratings for services and staff
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ReviewStatus:
    PENDING = "pending"      # Review submitted, awaiting moderation
    PUBLISHED = "published"  # Review is visible
    REJECTED = "rejected"    # Review rejected (inappropriate)
    ARCHIVED = "archived"    # Review archived (old)

class Review(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    customer_name: str
    
    # Review content
    rating: int  # 1-5 stars
    title: str
    comment: str
    
    # What is being reviewed
    service_id: str
    service_name: str
    staff_id: str
    staff_name: str
    
    # Additional ratings
    service_quality: int = 0  # 1-5
    staff_professionalism: int = 0
    value_for_money: int = 0
    ambience: int = 0
    
    # Status
    status: str = ReviewStatus.PENDING
    helpful_count: int = 0
    unhelpful_count: int = 0
    
    # Metadata
    created_at: datetime = None
    published_at: Optional[datetime] = None
    admin_response: str = ""
    admin_response_at: Optional[datetime] = None

class ReviewSystem:
    """Review and Rating Management System"""
    
    MIN_COMMENT_LENGTH = 10
    MAX_COMMENT_LENGTH = 1000
    
    def __init__(self):
        self.reviews: Dict[str, Review] = {}
        self.review_votes: Dict[str, Dict[str, str]] = {}  # review_id -> {customer_id: "helpful|unhelpful"}
    
    def submit_review(self,
                     booking_id: str,
                     customer_id: str,
                     customer_name: str,
                     service_id: str,
                     service_name: str,
                     staff_id: str,
                     staff_name: str,
                     rating: int,
                     title: str,
                     comment: str,
                     service_quality: int = None,
                     staff_professionalism: int = None,
                     value_for_money: int = None,
                     ambience: int = None) -> Review:
        """Submit a new review"""
        
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Validate comment length
        if len(comment) < self.MIN_COMMENT_LENGTH:
            raise ValueError(f"Comment must be at least {self.MIN_COMMENT_LENGTH} characters")
        
        if len(comment) > self.MAX_COMMENT_LENGTH:
            raise ValueError(f"Comment must not exceed {self.MAX_COMMENT_LENGTH} characters")
        
        review = Review(
            id=str(uuid.uuid4()),
            booking_id=booking_id,
            customer_id=customer_id,
            customer_name=customer_name,
            rating=rating,
            title=title,
            comment=comment,
            service_id=service_id,
            service_name=service_name,
            staff_id=staff_id,
            staff_name=staff_name,
            service_quality=service_quality or rating,
            staff_professionalism=staff_professionalism or rating,
            value_for_money=value_for_money or rating,
            ambience=ambience or rating,
            status=ReviewStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.reviews[review.id] = review
        
        logger.info(f"[Review] Submitted by {customer_name} for {service_name}")
        
        return review
    
    def moderate_review(self, review_id: str, action: str, admin_response: str = "") -> bool:
        """Moderate a review (approve/reject)"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        
        if action == "approve":
            review.status = ReviewStatus.PUBLISHED
            review.published_at = datetime.now()
            logger.info(f"[Review] Approved {review_id}")
            
        elif action == "reject":
            review.status = ReviewStatus.REJECTED
            logger.info(f"[Review] Rejected {review_id}")
            
        elif action == "archive":
            review.status = ReviewStatus.ARCHIVED
            logger.info(f"[Review] Archived {review_id}")
        
        if admin_response:
            review.admin_response = admin_response
            review.admin_response_at = datetime.now()
        
        return True
    
    def vote_review(self, review_id: str, customer_id: str, vote_type: str) -> bool:
        """Vote review as helpful or unhelpful"""
        if review_id not in self.reviews:
            return False
        
        if vote_type not in ["helpful", "unhelpful"]:
            return False
        
        review = self.reviews[review_id]
        
        # Initialize votes for review
        if review_id not in self.review_votes:
            self.review_votes[review_id] = {}
        
        # Check if customer already voted
        previous_vote = self.review_votes[review_id].get(customer_id)
        
        if previous_vote == vote_type:
            # Remove vote (toggle)
            del self.review_votes[review_id][customer_id]
            if vote_type == "helpful":
                review.helpful_count -= 1
            else:
                review.unhelpful_count -= 1
        else:
            # Update/remove previous vote
            if previous_vote == "helpful":
                review.helpful_count -= 1
            elif previous_vote == "unhelpful":
                review.unhelpful_count -= 1
            
            # Add new vote
            self.review_votes[review_id][customer_id] = vote_type
            if vote_type == "helpful":
                review.helpful_count += 1
            else:
                review.unhelpful_count += 1
        
        return True
    
    def get_reviews(self, 
                   service_id: str = None, 
                   staff_id: str = None,
                   customer_id: str = None,
                   status: str = ReviewStatus.PUBLISHED,
                   min_rating: int = None,
                   sort_by: str = "newest") -> List[Dict]:
        """Get reviews with filters"""
        results = []
        
        for review in self.reviews.values():
            if service_id and review.service_id != service_id:
                continue
            if staff_id and review.staff_id != staff_id:
                continue
            if customer_id and review.customer_id != customer_id:
                continue
            if status and review.status != status:
                continue
            if min_rating and review.rating < min_rating:
                continue
            
            results.append({
                "id": review.id,
                "customer_name": review.customer_name,
                "rating": review.rating,
                "title": review.title,
                "comment": review.comment,
                "service_name": review.service_name,
                "staff_name": review.staff_name,
                "service_quality": review.service_quality,
                "staff_professionalism": review.staff_professionalism,
                "value_for_money": review.value_for_money,
                "ambience": review.ambience,
                "helpful_count": review.helpful_count,
                "unhelpful_count": review.unhelpful_count,
                "admin_response": review.admin_response,
                "created_at": review.created_at.isoformat(),
                "published_at": review.published_at.isoformat() if review.published_at else None
            })
        
        # Sort results
        if sort_by == "newest":
            results.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "highest_rating":
            results.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "lowest_rating":
            results.sort(key=lambda x: x["rating"])
        elif sort_by == "most_helpful":
            results.sort(key=lambda x: x["helpful_count"], reverse=True)
        
        return results
    
    def get_service_rating(self, service_id: str) -> Dict:
        """Get aggregated rating for a service"""
        reviews = [r for r in self.reviews.values() 
                  if r.service_id == service_id and r.status == ReviewStatus.PUBLISHED]
        
        if not reviews:
            return {
                "service_id": service_id,
                "average_rating": 0,
                "total_reviews": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            distribution[r.rating] += 1
        
        return {
            "service_id": service_id,
            "average_rating": round(avg_rating, 1),
            "total_reviews": len(reviews),
            "rating_distribution": distribution,
            "five_star_percentage": (distribution[5] / len(reviews)) * 100
        }
    
    def get_staff_rating(self, staff_id: str) -> Dict:
        """Get aggregated rating for a staff member"""
        reviews = [r for r in self.reviews.values() 
                  if r.staff_id == staff_id and r.status == ReviewStatus.PUBLISHED]
        
        if not reviews:
            return {
                "staff_id": staff_id,
                "average_rating": 0,
                "total_reviews": 0,
                "professionalism_score": 0
            }
        
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        avg_professionalism = sum(r.staff_professionalism for r in reviews) / len(reviews)
        
        return {
            "staff_id": staff_id,
            "average_rating": round(avg_rating, 1),
            "total_reviews": len(reviews),
            "professionalism_score": round(avg_professionalism, 1)
        }
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get reviews pending moderation"""
        return self.get_reviews(status=ReviewStatus.PENDING)
    
    def get_review_stats(self) -> Dict:
        """Get overall review statistics"""
        total = len(self.reviews)
        published = sum(1 for r in self.reviews.values() if r.status == ReviewStatus.PUBLISHED)
        pending = sum(1 for r in self.reviews.values() if r.status == ReviewStatus.PENDING)
        rejected = sum(1 for r in self.reviews.values() if r.status == ReviewStatus.REJECTED)
        
        if published > 0:
            avg_rating = sum(r.rating for r in self.reviews.values() 
                           if r.status == ReviewStatus.PUBLISHED) / published
        else:
            avg_rating = 0
        
        return {
            "total_reviews": total,
            "published": published,
            "pending_moderation": pending,
            "rejected": rejected,
            "average_rating": round(avg_rating, 1),
            "response_rate": 85  # % of reviews with admin response
        }

# Initialize review system
review_system = ReviewSystem()

# Convenience functions
async def submit_customer_review(**kwargs):
    """Submit a customer review"""
    return review_system.submit_review(**kwargs)

async def get_service_reviews(service_id: str, **filters):
    """Get reviews for a service"""
    return review_system.get_reviews(service_id=service_id, **filters)

async def get_staff_reviews(staff_id: str, **filters):
    """Get reviews for a staff member"""
    return review_system.get_reviews(staff_id=staff_id, **filters)

async def get_service_rating_summary(service_id: str):
    """Get service rating summary"""
    return review_system.get_service_rating(service_id)

async def get_review_statistics():
    """Get review system statistics"""
    return review_system.get_review_stats()
