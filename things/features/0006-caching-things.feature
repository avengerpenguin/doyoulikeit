Feature: Reduce round trips to DBPedia when people visit pages

  Scenario: User fetches a page that someone else has recently accessed
    Given someone else has recently visited the page for "New Kids on the Block"
    When I visit the page for "New Kids on the Block"
    Then the page should load quickly for me without a call to DBPedia
