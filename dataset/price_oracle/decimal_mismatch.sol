// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Oracle Decimal Mismatch (Off-by-1e12 Price Error)
 * CATEGORY: Price Oracle — Incorrect Scaling / Unit Confusion
 *
 * Chainlink BTC/USD returns an answer with 8 decimals.
 * USDC has 6 decimals. The protocol assumes both are 18 decimals,
 * resulting in a BTC price that is 10^10 times too large.
 * An attacker deposits 1 USDC (1e6 units), gets priced as if it's
 * 1e18 USDC due to wrong scaling, then borrows the entire protocol.
 */
interface IChainlink {
    function latestRoundData() external view
        returns (uint80, int256, uint256, uint256, uint80);
    function decimals() external view returns (uint8);
}

contract DecimalMismatch {
    IChainlink public btcUsdFeed;
    // BUG: assumes both feed and internal accounting use 18 decimals
    uint256 public constant ASSUMED_DECIMALS = 1e18;

    constructor(address _feed) {
        btcUsdFeed = IChainlink(_feed);
    }

    function getBtcPriceUsd() public view returns (uint256) {
        (, int256 answer,,,) = btcUsdFeed.latestRoundData();
        require(answer > 0, "Bad price");
        // BUG: feed has 8 decimals, not 18 — price is 10^10 times too large
        return uint256(answer); // should be: uint256(answer) * 1e10
    }

    // amount in USDC (6 decimals), price in BTC/USD (8 decimals → scaled wrong)
    function usdcToBtc(uint256 usdcAmount) external view returns (uint256) {
        uint256 btcPrice = getBtcPriceUsd();
        // BUG: units completely mismatched — result is off by 10^22
        return (usdcAmount * ASSUMED_DECIMALS) / btcPrice;
    }

    function maxBorrow(uint256 usdcCollateral) external view returns (uint256) {
        // BUG: wildly inflated collateral value → attacker borrows entire protocol
        return usdcToBtc(usdcCollateral) * 75 / 100;
    }
}
