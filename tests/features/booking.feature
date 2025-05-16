Feature: Event Booking
  As a user
  I want to book tickets for events
  So that I can attend them

  Background:
    Given there is an event "Summer Concert" at "Concert Hall"
    And the event has a session on "2025-06-01 19:00" with 100 seats at $50.00

  Scenario: Successfully book tickets
    Given I am a registered user
    When I try to book 2 seats for the session
    Then the booking should be created successfully
    And the booking status should be "PENDING"
    And the session should have 98 available seats
    And the price per seat should be $50.00

  Scenario: Book tickets when capacity is nearly full
    Given I am a registered user
    And 80 seats are already booked for the session
    When I try to book 2 seats for the session
    Then the booking should be created successfully
    And the price per seat should be $75.00
    And the session should have 18 available seats

  Scenario: Try to book more seats than available
    Given I am a registered user
    And 95 seats are already booked for the session
    When I try to book 10 seats for the session
    Then I should get an "insufficient seats" error
    And the session should have 5 available seats

  Scenario: Cancel a booking
    Given I am a registered user
    And I have a confirmed booking for 2 seats
    When I cancel my booking
    Then the booking status should be "CANCELLED"
    And the session should have 100 available seats

  Scenario: Dynamic pricing based on occupancy
    Given I am a registered user
    When I book seats with the following occupancy rates:
      | occupancy | seats | expected_price |
      | 0%       | 10    | $50.00         |
      | 60%      | 10    | $60.00         |
      | 80%      | 5     | $75.00         |
    Then all bookings should have the correct prices 