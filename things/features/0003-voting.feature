Feature: Voting on things

Scenario: Liking something
  Given I am a registered user
  When I visit the page for "Saturnalia"
  And I click the "Yes" button
  Then the site should register my like for "Saturnalia"

Scenario: Can't like something twice
  Given I am a registered user
  And I have previously liked "Roman Empire"
  When I visit the page for "Roman Empire"
  Then there should be no "Yes" button

Scenario: Unregistered visitors can still vote temporarily
  Given I am a new visitor
  When I visit the page for "Cleopatra"
  And I click the "Yes" button
  Then the site should register my like for "Cleopatra"
