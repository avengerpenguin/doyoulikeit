Feature: New users registering with username and password

  Scenario: Registration process
    Given I am not a registered user
    When I click the 'Register' link
    And I give a username and password
    Then I should be logged in

  Scenario: Username already taken
    Given I am not a registered user
    When I try to register with an existing username
    Then I should get an error messaging explaining that username is taken

  Scenario: User that has voted anonymously keeps votes when they register
    Given I am not a registered user
    But I have been voting on some things anonymously
    When I register successfully
    Then my anonymous votes should be linked to my new account
