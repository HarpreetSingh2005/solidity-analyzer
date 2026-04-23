// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnMissingPriceValidation {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Does not check if the price is > 0
    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        // Casting negative price to uint256 causes massive overflow logically
        return uint256(price);
    }
}