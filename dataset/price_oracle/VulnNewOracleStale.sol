// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: No check for stale oracle price.
contract VulnNewOracleStale {
    AggregatorV3Interface public priceFeed;
    function getPrice() public view returns (int256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return price; // Price might be hours/days old
    }
}