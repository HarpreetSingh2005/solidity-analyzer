// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Stale Chainlink Price (No Freshness Check)
 * CATEGORY: Price Oracle — Staleness / Missing Validation
 *
 * The Chainlink aggregator is called but the updatedAt timestamp is
 * never checked. During network congestion or Chainlink downtime the
 * oracle may go hours without an update. Any protocol using this price
 * will operate on arbitrarily stale data — enabling profitable liquidations
 * or over-borrowing against an out-of-date valuation.
 */
interface AggregatorV3Interface {
    function latestRoundData() external view returns (
        uint80 roundId, int256 answer, uint256 startedAt,
        uint256 updatedAt, uint80 answeredInRound
    );
    function decimals() external view returns (uint8);
}

contract StaleChainlink {
    AggregatorV3Interface public immutable priceFeed;
    uint256 public constant MAX_STALENESS = 1 hours; // defined but never enforced

    constructor(address _feed) {
        priceFeed = AggregatorV3Interface(_feed);
    }

    function getPrice() public view returns (int256) {
        (
            uint80  roundId,
            int256  answer,
            ,
            uint256 updatedAt,
            uint80  answeredInRound
        ) = priceFeed.latestRoundData();

        require(answer > 0, "Negative price");
        // BUG: no staleness check — updatedAt could be days ago
        // FIX: require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");

        // BUG: no round completeness check
        // FIX: require(answeredInRound >= roundId, "Incomplete round");

        return answer;
    }

    function assetValue(uint256 amount) external view returns (uint256) {
        int256 price = getPrice();
        return (amount * uint256(price)) / (10 ** priceFeed.decimals());
    }
}
