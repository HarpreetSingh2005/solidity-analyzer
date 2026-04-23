// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
interface AggregatorV3Interface {
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
}
contract StaleChainlink {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (int256) {
        (, int256 answer,,,) = feed.latestRoundData();
        return answer; // BUG: no staleness check
    }
}