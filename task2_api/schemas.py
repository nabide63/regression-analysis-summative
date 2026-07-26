"""
Pydantic request/response models for my milk yield API.

I set the min/max bounds on every numeric field to the actual min/max I saw
in the 250,000-row training set (check the df.describe().T cell in the
notebook). I did this on purpose so predictions stay inside the range the
model was actually trained on, instead of letting someone send in a value
like a 900kg cow that the LinearRegression pipeline never saw during training.

For the vaccine flags and categorical fields (breed, season, etc.) I used
Literal, which makes FastAPI do a type check AND restrict it to an enum of
allowed values (shows up as dropdowns in Swagger UI). So a bad request,
whether it's the wrong type or an unknown category, gets rejected with a 422
before it even reaches my model.
"""

from typing import Literal

from pydantic import BaseModel, Field

from features import (
    BREED_CATEGORIES,
    CLIMATE_ZONE_CATEGORIES,
    FEED_TYPE_CATEGORIES,
    LACTATION_STAGE_CATEGORIES,
    MANAGEMENT_SYSTEM_CATEGORIES,
    SEASON_CATEGORIES,
)

VaccineFlag = Literal[0, 1]


class CowFeatures(BaseModel):
    # --- Numeric features ---
    Age_Months: int = Field(..., ge=24, le=143, description="Cow's age in months")
    Weight_kg: float = Field(..., ge=250.0, le=750.0, description="Body weight in kg")
    Parity: int = Field(..., ge=1, le=6, description="Number of times the cow has calved")
    Days_in_Milk: int = Field(..., ge=1, le=364, description="Days since the current lactation started")
    Feed_Quantity_kg: float = Field(..., ge=3.0, le=25.0, description="Daily feed quantity in kg")
    Feeding_Frequency: int = Field(..., ge=1, le=5, description="Feedings per day")
    Water_Intake_L: float = Field(..., ge=20.0, le=120.0, description="Daily water intake in litres")
    Walking_Distance_km: float = Field(..., ge=0.5, le=12.0, description="Daily walking distance in km")
    Grazing_Duration_hrs: float = Field(..., ge=1.0, le=14.0, description="Hours spent grazing per day")
    Rumination_Time_hrs: float = Field(..., ge=4.0, le=14.0, description="Hours spent ruminating per day")
    Resting_Hours: float = Field(..., ge=5.0, le=18.0, description="Hours spent resting per day")
    Ambient_Temperature_C: float = Field(..., ge=-10.0, le=45.0, description="Ambient temperature in Celsius")
    Humidity_percent: float = Field(..., ge=10.0, le=100.0, description="Relative humidity percentage")
    Housing_Score: float = Field(..., ge=0.3, le=1.0, description="Housing quality score (0.3-1.0)")
    FMD_Vaccine: VaccineFlag = Field(..., description="Foot-and-mouth disease vaccine: 0=no, 1=yes")
    Brucellosis_Vaccine: VaccineFlag = Field(..., description="Brucellosis vaccine: 0=no, 1=yes")
    HS_Vaccine: VaccineFlag = Field(..., description="Haemorrhagic septicaemia vaccine: 0=no, 1=yes")
    BQ_Vaccine: VaccineFlag = Field(..., description="Black quarter vaccine: 0=no, 1=yes")
    Anthrax_Vaccine: VaccineFlag = Field(..., description="Anthrax vaccine: 0=no, 1=yes")
    IBR_Vaccine: VaccineFlag = Field(..., description="Infectious bovine rhinotracheitis vaccine: 0=no, 1=yes")
    BVD_Vaccine: VaccineFlag = Field(..., description="Bovine viral diarrhea vaccine: 0=no, 1=yes")
    Rabies_Vaccine: VaccineFlag = Field(..., description="Rabies vaccine: 0=no, 1=yes")
    Previous_Week_Avg_Yield: float = Field(..., ge=0.0, le=38.67, description="Previous week's average daily yield in litres")
    Body_Condition_Score: float = Field(..., ge=2.0, le=5.0, description="Body condition score (2.0-5.0)")
    Milking_Interval_hrs: int = Field(..., ge=6, le=24, description="Hours between milkings")

    # --- Categorical features ---
    Breed: Literal[tuple(BREED_CATEGORIES)] = Field(..., description="Cattle breed")
    Climate_Zone: Literal[tuple(CLIMATE_ZONE_CATEGORIES)] = Field(..., description="Climate zone the farm is in")
    Management_System: Literal[tuple(MANAGEMENT_SYSTEM_CATEGORIES)] = Field(..., description="Farm management system")
    Lactation_Stage: Literal[tuple(LACTATION_STAGE_CATEGORIES)] = Field(..., description="Current lactation stage")
    Feed_Type: Literal[tuple(FEED_TYPE_CATEGORIES)] = Field(..., description="Primary feed type")
    Season: Literal[tuple(SEASON_CATEGORIES)] = Field(..., description="Current season")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Age_Months": 48,
                "Weight_kg": 480.0,
                "Parity": 3,
                "Days_in_Milk": 120,
                "Feed_Quantity_kg": 14.5,
                "Feeding_Frequency": 3,
                "Water_Intake_L": 70.0,
                "Walking_Distance_km": 4.0,
                "Grazing_Duration_hrs": 6.0,
                "Rumination_Time_hrs": 8.0,
                "Resting_Hours": 10.0,
                "Ambient_Temperature_C": 24.0,
                "Humidity_percent": 55.0,
                "Housing_Score": 0.7,
                "FMD_Vaccine": 1,
                "Brucellosis_Vaccine": 1,
                "HS_Vaccine": 0,
                "BQ_Vaccine": 0,
                "Anthrax_Vaccine": 1,
                "IBR_Vaccine": 0,
                "BVD_Vaccine": 0,
                "Rabies_Vaccine": 1,
                "Previous_Week_Avg_Yield": 9.2,
                "Body_Condition_Score": 3.5,
                "Milking_Interval_hrs": 12,
                "Breed": "Holstein-Friesian",
                "Climate_Zone": "Tropical",
                "Management_System": "Mixed",
                "Lactation_Stage": "Mid",
                "Feed_Type": "Mixed_Feed",
                "Season": "Summer",
            }
        }
    }


class PredictionResponse(BaseModel):
    predicted_milk_yield_l: float = Field(..., description="Predicted daily milk yield in litres")


class RetrainResponse(BaseModel):
    message: str
    rows_added: int
    total_training_rows: int
    train_r2: float
    test_r2: float
    test_rmse: float
