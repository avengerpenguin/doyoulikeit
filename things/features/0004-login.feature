Feature: Existing users can log in

  Scenario: Non-logged-in user can log in with username and password
    Given I am a registered user
    But I am not logged in
    When I visit any page
    And click the "Log in" link
    And give my username and password
    Then I should be taken back to my original page
    And I should be logged in
