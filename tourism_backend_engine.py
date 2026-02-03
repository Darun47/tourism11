import pandas as pd
import numpy as np
import ast
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TouristProfile:
    """Tourist profile data model"""
    age: int
    interests: List[str]
    accessibility_needs: bool
    preferred_duration: int
    budget_preference: str  # 'Budget', 'Mid-range', 'Luxury'
    climate_preference: Optional[str] = None  # 'Cold', 'Temperate', 'Warm'
    season_preference: Optional[str] = None  # 'Spring', 'Summer', 'Autumn', 'Winter'
    
    def __post_init__(self):
        """Validate tourist profile"""
        if self.age < 18 or self.age > 100:
            raise ValueError(f"Age must be between 18 and 100, got {self.age}")
        if self.preferred_duration < 1:
            raise ValueError(f"Duration must be at least 1 day, got {self.preferred_duration}")

@dataclass
class Destination:
    """Destination data model"""
    record_id: str
    city: str
    country: str
    site_name: str
    avg_cost_usd: float
    best_season: str
    climate: str
    culture_score: float
    adventure_score: float
    nature_score: float
    avg_rating: float
    unesco_site: bool
    
@dataclass
@@ -223,50 +224,54 @@ class TourismBackendEngine:
            },
            'recommendations': {
                'best_season': self._get_best_season(selected_destinations),
                'packing_tips': self._get_packing_tips(selected_destinations, tourist_profile),
                'accessibility_info': self._get_accessibility_info(selected_destinations) if tourist_profile.accessibility_needs else None
            }
        }
        
        print(f"✓ Generated {len(itinerary_days)}-day itinerary")
        print(f"✓ Total cost: ${total_cost:,.2f}")
        print(f"✓ Cities: {', '.join(result['itinerary']['cities_visited'])}")
        
        return result
    
    def _filter_by_preferences(self, profile: TouristProfile) -> pd.DataFrame:
        """Filter destinations by tourist preferences"""
        df = self.df.copy()
        
        # Filter by budget
        if profile.budget_preference:
            df = df[df['budget_level'] == profile.budget_preference]
        
        # Filter by climate preference
        if profile.climate_preference:
            df = df[df['climate_classification'] == profile.climate_preference]

        # Filter by season preference
        if profile.season_preference and 'Best Season' in df.columns:
            df = df[df['Best Season'] == profile.season_preference]
        
        # Filter by accessibility if needed
        # Note: This would require accessibility data in the dataset
        
        return df
    
    def _score_destinations(
        self, 
        df: pd.DataFrame, 
        profile: TouristProfile
    ) -> pd.DataFrame:
        """
        Score destinations based on tourist interests
        
        Uses a weighted scoring system:
        - Interest match: 40%
        - Rating: 30%
        - Experience scores: 30%
        """
        df = df.copy()
        
        # Score 1: Interest match (0-100)
        def calc_interest_match(row):
            row_interests = row.get('Interests', [])
            if not isinstance(row_interests, list) or not profile.interests:
