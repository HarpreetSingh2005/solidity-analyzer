// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Assuming 18 decimals for oracle, leading to incorrect calculations.
contract VulnNewOracleDecimals {
    AggregatorV3Interface public feed;
    function getCollateralValue(uint256 amount) public view returns (uint256) {
        (, int256 price, , , ) = feed.latestRoundData();
        return (amount * uint256(price)) / 1e18; // Chainlink USD feeds use 8 decimals, not 18
    }
}