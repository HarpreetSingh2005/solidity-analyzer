// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnL2Sequencer {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Missing check if L2 sequencer is down (Arbitrum/Optimism)
    function getPrice() public view returns (int256) {
        (, int256 price, , uint256 updatedAt, ) = priceFeed.latestRoundData();
        require(block.timestamp - updatedAt < 1 hours, "Stale price");
        return price;
    }
}