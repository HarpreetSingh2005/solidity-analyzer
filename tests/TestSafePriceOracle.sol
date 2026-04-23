// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

// @notice Safe oracle consumption with full validation.
contract TestSafePriceOracle {
    AggregatorV3Interface public priceFeed;

    constructor(address _feed) {
        priceFeed = AggregatorV3Interface(_feed);
    }

    function getPrice() public view returns (uint256) {
        (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
        
        // Safe: Validating against staleness and negative values
        require(price > 0, "Invalid price");
        require(block.timestamp - updatedAt < 3600, "Stale price");
        require(answeredInRound >= roundId, "Stale round");

        return uint256(price);
    }
}