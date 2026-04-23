// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnWrongDecimals {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Assuming 18 decimals for Chainlink oracle (usually 8 for non-ETH pairs)
    function calculateValue(uint256 amount) public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        // Assuming price is 1e18, but it might be 1e8!
        return (amount * uint256(price)) / 1e18;
    }
}