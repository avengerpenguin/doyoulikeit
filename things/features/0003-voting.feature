Feature: Existing users can vote on things they like

Scenario: User likes something
  Given I am an existing user already logged in
  When I visit the page for The Netherlands
  And I click the "like" button
  Then my vote should be registered
