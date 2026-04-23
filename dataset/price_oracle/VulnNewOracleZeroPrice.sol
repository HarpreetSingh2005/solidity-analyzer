// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Missing check for price <= 0.
contract VulnNewOracleZeroPrice {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = feed.latestRoundData();
        return uint256(price); // If price drops below 0, it wraps to massive uint256
    }
}