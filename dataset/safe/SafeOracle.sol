// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

// @notice Safe Oracle implementation enforcing strict checks on answered round and staleness.
contract SafeOracle {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function getLatestPrice() public view returns (int256) {
        (
            uint80 roundID, 
            int price,
            ,
            uint timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        require(price > 0, "Negative or zero price");
        require(timeStamp > 0, "Round not complete");
        require(answeredInRound >= roundID, "Stale price");
        require(block.timestamp - timeStamp < 1 hours, "Price too old");

        return price;
    }
}