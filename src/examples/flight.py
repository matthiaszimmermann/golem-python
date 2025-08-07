"""Example of using Pydantic for flight time handling."""

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field

UTC: timezone = timezone(offset=timedelta(hours=0))


class Flight(BaseModel):
    """Represents a flight with departure time and duration."""

    # Departure information
    departure_airport: str = Field(..., min_length=3, max_length=3)
    departure_time: datetime
    departure_utc_offset: int = Field(..., ge=-12, le=14)  # Hours from UTC

    # Arrival information
    arrival_airport: str = Field(..., min_length=3, max_length=3)
    arrival_utc_offset: int = Field(..., ge=-12, le=14)  # Hours from UTC

    # Flight duration
    duration_minutes: int = Field(..., gt=0)

    @classmethod
    def datetime_utc(
        cls, year: int, month: int, day: int, hour: int, minute: int = 0
    ) -> datetime:
        """Provide a UTC datetime for the provided parameter values."""
        return datetime(year, month, day, hour, minute, tzinfo=UTC)

    def calculate_arrival_time(self) -> datetime:
        """Calculate arrival time based on departure time and duration."""
        return self.departure_time + timedelta(minutes=self.duration_minutes)

    def to_local_times(self) -> dict[str, datetime]:
        """Convert times to their respective timezones."""
        departure_local = self.departure_time + timedelta(
            hours=self.departure_utc_offset
        )
        arrival_local = self.calculate_arrival_time() + timedelta(
            hours=self.arrival_utc_offset
        )

        return {
            "departure_local": departure_local,
            "arrival_local": arrival_local,
        }


def main() -> None:
    """Demo using flight from New York to London."""
    flight = Flight(
        # Departure information
        departure_airport="JFK",
        departure_time=Flight.datetime_utc(2024, 3, 25, 20, 0),  # 8 PM
        departure_utc_offset=-4,  # EDT (UTC-4)
        # Arrival information
        arrival_airport="LHR",
        arrival_utc_offset=0,  # GMT (UTC+0)
        # Flight duration
        duration_minutes=420,  # 7 hours
    )

    # Calculate arrival time
    arrival_time = flight.calculate_arrival_time()
    print(f"Arrival time: {arrival_time}")

    # Get local times
    local_times = flight.to_local_times()
    print(f"Departure (local): {local_times['departure_local']}")
    print(f"Arrival (local): {local_times['arrival_local']}")


if __name__ == "__main__":
    main()
