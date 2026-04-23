// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: L2 specific - missing check if the L2 sequencer is down before using price.
contract VulnNewOracleSequencer {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (int256) {
        // Fails to check Arbitrum/Optimism sequencer uptime feed
        (, int256 price, , uint256 updatedAt, ) = feed.latestRoundData();
        require(block.timestamp - updatedAt < 3600, "Stale");
        return price;
    }
}