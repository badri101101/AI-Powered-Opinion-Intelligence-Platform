from datetime import datetime, timedelta
from typing import List
import numpy as np
from sklearn.linear_model import LinearRegression
from app.schemas.metrics import ForecastResult, TimeSeriesPoint, ProjectedForecastPoint

class ForecastingEngine:
    def forecast(self, time_series: List[TimeSeriesPoint]) -> ForecastResult:
        """Performs statistical regression and momentum projection on historical time-series data."""
        if len(time_series) < 3:
            return ForecastResult(
                available=False,
                trend_direction="INSUFFICIENT_DATA",
                slope=0.0,
                confidence="UNAVAILABLE",
                reason="Insufficient historical time-series data points (minimum 3 required) to compute an objective forecast",
                projected_points=[]
            )

        try:
            # Prepare numeric features: X = day indices (0, 1, 2, ...), y = sentiment scores
            x_vals = np.array(range(len(time_series))).reshape(-1, 1)
            y_vals = np.array([pt.sentiment_score for pt in time_series])

            model = LinearRegression()
            model.fit(x_vals, y_vals)
            slope = float(model.coef_[0])
            intercept = float(model.intercept_)

            # Calculate residual variance for confidence bounds
            predictions = model.predict(x_vals)
            residuals = y_vals - predictions
            std_err = float(np.std(residuals)) if len(residuals) > 0 else 0.1

            # Determine direction
            if slope > 0.02:
                direction = "UPWARD"
            elif slope < -0.02:
                direction = "DOWNWARD"
            else:
                direction = "STABLE"

            # Confidence determination
            if std_err < 0.15 and len(time_series) >= 5:
                confidence = "HIGH"
            elif std_err < 0.3 or len(time_series) >= 3:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            # Generate 3 future daily projections
            last_date_str = time_series[-1].date
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
            projected_pts: List[ProjectedForecastPoint] = []

            for i in range(1, 4):
                next_date = (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
                future_idx = len(time_series) - 1 + i
                pred_val = float(np.clip(intercept + slope * future_idx, -1.0, 1.0))
                
                projected_pts.append(ProjectedForecastPoint(
                    date=next_date,
                    projected_sentiment=round(pred_val, 2),
                    confidence_lower=round(float(np.clip(pred_val - 1.96 * std_err, -1.0, 1.0)), 2),
                    confidence_upper=round(float(np.clip(pred_val + 1.96 * std_err, -1.0, 1.0)), 2)
                ))

            reason = f"Calculated linear regression momentum (slope: {slope:+.4f}) across {len(time_series)} intervals."
            return ForecastResult(
                available=True,
                trend_direction=direction,
                slope=round(slope, 4),
                confidence=confidence,
                reason=reason,
                projected_points=projected_pts
            )

        except Exception as e:
            return ForecastResult(
                available=False,
                trend_direction="UNAVAILABLE",
                slope=0.0,
                confidence="UNAVAILABLE",
                reason=f"Forecasting computation failed: {str(e)}",
                projected_points=[]
            )

forecasting_engine = ForecastingEngine()
