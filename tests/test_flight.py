"""Tests for the Flight class."""

import pytest

from examples.flight import Flight


def test_valid_flight() -> None:
    """Test creating a valid flight."""
    flight = Flight(
        # Departure information
        departure_airport="ZRH",
        departure_time=Flight.datetime_utc(2024, 3, 25, 13, 30),  # 13:30
        departure_utc_offset=1,  # CET (UTC+1)
        # Arrival information
        arrival_airport="BKK",
        arrival_utc_offset=7,  # ICT (UTC+7)
        # Flight duration
        duration_minutes=640,  # 10h40m
    )

    assert flight.departure_airport == "ZRH"
    assert flight.arrival_airport == "BKK"
    assert flight.duration_minutes == 640


def test_invalid_airport_code() -> None:
    """Test invalid airport code length."""
    with pytest.raises(ValueError, match="String should have at most 3 characters"):
        Flight(
            # Departure information
            departure_airport="ZRHX",  # Too long
            departure_time=Flight.datetime_utc(2024, 3, 25, 13, 30),
            departure_utc_offset=1,
            # Arrival information
            arrival_airport="BKK",
            arrival_utc_offset=7,
            # Flight duration
            duration_minutes=640,
        )


def test_invalid_utc_offset() -> None:
    """Test invalid UTC offset."""
    with pytest.raises(ValueError, match="Input should be less than or equal to 14"):
        Flight(
            # Departure information
            departure_airport="ZRH",
            departure_time=Flight.datetime_utc(2024, 3, 25, 13, 30),
            departure_utc_offset=15,  # Invalid offset
            # Arrival information
            arrival_airport="BKK",
            arrival_utc_offset=7,
            # Flight duration
            duration_minutes=640,
        )


def test_arrival_time_calculation() -> None:
    """Test arrival time calculation."""
    flight = Flight(
        # Departure information
        departure_airport="ZRH",
        departure_time=Flight.datetime_utc(2024, 3, 25, 13, 30),
        departure_utc_offset=1,
        # Arrival information
        arrival_airport="BKK",
        arrival_utc_offset=7,
        # Flight duration
        duration_minutes=640,
    )

    expected_arrival = Flight.datetime_utc(2024, 3, 26, 0, 10)  # 10h40m after departure
    assert flight.calculate_arrival_time() == expected_arrival


def test_local_times() -> None:
    """Test local time conversion."""
    flight = Flight(
        # Departure information
        departure_airport="ZRH",
        departure_time=Flight.datetime_utc(2024, 3, 25, 13, 30),
        departure_utc_offset=1,
        # Arrival information
        arrival_airport="BKK",
        arrival_utc_offset=7,
        # Flight duration
        duration_minutes=640,
    )

    local_times = flight.to_local_times()
    assert local_times["departure_local"].hour == 14  # 13:30 + 1 hour UTC offset
    assert local_times["arrival_local"].hour == 7  # 00:10 + 7 hours UTC offset
