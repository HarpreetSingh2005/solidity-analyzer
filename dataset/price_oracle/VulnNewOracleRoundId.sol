// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Missing check if answeredInRound >= roundId.
contract VulnNewOracleRoundId {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (int256) {
        (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) = feed.latestRoundData();
        require(block.timestamp - updatedAt < 3600, "Stale");
        // Missing: require(answeredInRound >= roundId, "Stale round");
        return price;
    }
}