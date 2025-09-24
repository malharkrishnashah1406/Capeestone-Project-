from typing import List, Optional
from .models import Event, EventType, FinancialMetric, ImpactPrediction
from .event_collector import EventCollector
from .predictor import ImpactPredictor

class ImpactPredictionSystem:
    def __init__(self):
        self.event_collector = EventCollector()
        self.predictor = ImpactPredictor()
        
        # Define financial metrics
        self.financial_metrics = [
            FinancialMetric(
                name="Total Revenue",
                description="Total income generated from business operations",
                category="Revenue"
            ),
            FinancialMetric(
                name="Net Profit",
                description="Total profit after all expenses",
                category="Profit"
            ),
            FinancialMetric(
                name="Valuation",
                description="Company's estimated market value",
                category="Valuation"
            ),
            FinancialMetric(
                name="Market Share",
                description="Percentage of total market controlled",
                category="Market"
            ),
            FinancialMetric(
                name="Customer Acquisition Cost",
                description="Cost to acquire a new customer",
                category="Customer"
            ),
            FinancialMetric(
                name="Funding Availability",
                description="Ease of accessing capital",
                category="Funding"
            ),
            FinancialMetric(
                name="Operating Expenses",
                description="Costs of running the business",
                category="Operations"
            ),
            FinancialMetric(
                name="Employee Retention",
                description="Ability to retain employees",
                category="HR"
            )
        ]
    
    def collect_and_analyze_events(
        self,
        query: str,
        days: int = 7,
        location: Optional[str] = None
    ) -> List[ImpactPrediction]:
        """Collect events and analyze their impact on financial metrics"""
        # Collect events
        events = self.event_collector.collect_news_events(
            query=query,
            days=days,
            location=location
        )
        
        # Analyze impact for each event and metric
        predictions = []
        for event in events:
            for metric in self.financial_metrics:
                prediction = self.predictor.predict_impact(event, metric)
                predictions.append(prediction)
        
        return predictions
    
    def print_analysis(self, predictions: List[ImpactPrediction]):
        """Print formatted analysis of predictions"""
        # Group predictions by event
        event_predictions = {}
        for prediction in predictions:
            if prediction.event.title not in event_predictions:
                event_predictions[prediction.event.title] = []
            event_predictions[prediction.event.title].append(prediction)
        
        # Print analysis for each event
        for event_title, event_preds in event_predictions.items():
            print(f"\n{'='*80}")
            print(f"Event: {event_title}")
            print(f"{'='*80}")
            
            # Sort predictions by impact score
            sorted_preds = sorted(
                event_preds,
                key=lambda x: abs(x.impact_score),
                reverse=True
            )
            
            # Print top 3 most significant impacts
            for pred in sorted_preds[:3]:
                print(f"\nMetric: {pred.metric.name}")
                print(f"Impact Score: {pred.impact_score:.2f}")
                print(f"Confidence: {pred.confidence:.2f}")
                print(f"Timeframe: {pred.timeframe}")
                print(f"Explanation: {pred.explanation}")
                print("-" * 40)

def main():
    # Initialize the system
    system = ImpactPredictionSystem()
    
    # Get News API key
    print("Welcome to the Startup Impact Prediction System")
    print("This system analyzes news events and predicts their impact on startup metrics.")
    print("\nPlease enter your News API key:")
    api_key = input("News API key: ")
    system.event_collector.set_news_api_key(api_key)
    
    # Get user input
    print("\nPlease enter the following information:")
    query = input("Search query (e.g., 'Indian startup'): ")
    days = int(input("Number of days to analyze (1-30): "))
    location = input("Location (optional, press Enter to skip): ")
    
    # Collect and analyze events
    print("\nCollecting and analyzing events...")
    predictions = system.collect_and_analyze_events(
        query=query,
        days=days,
        location=location if location else None
    )
    
    # Print analysis
    system.print_analysis(predictions)

if __name__ == "__main__":
    main() 