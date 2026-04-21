// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Oracle TWAP Stuffing via Flash Loan
 * CATEGORY: Flash Loan — TWAP Manipulation Through High-Volume Trading
 *
 * The TWAP oracle updates on every trade. By using a flash loan to execute
 * hundreds of trades in a loop within one transaction, an attacker can
 * set the cumulative price to any desired value. The TWAP then reflects
 * the attacker's chosen price for the entire window period, allowing
 * profitable borrowing during that window.
 */
contract OracleStuffing {
    uint256 public priceCumulative;
    uint256 public lastUpdateTime;
    uint256 public constant WINDOW = 10 minutes;

    constructor() {
        lastUpdateTime = block.timestamp;
    }

    // BUG: called by AMM on every trade — no volume or frequency limit
    function updatePrice(uint256 spotPrice) external {
        uint256 dt         = block.timestamp - lastUpdateTime;
        priceCumulative   += spotPrice * dt;
        lastUpdateTime     = block.timestamp;
    }

    // BUG: attacker can call updatePrice() many times in the same block
    // with different spotPrices (via flash loan → trade loop → each trade calls update)
    // Because dt=0 within same block, this particular example is muted BUT:
    // An attacker can do large trades across multiple blocks during the TWAP window
    // OR stuff the oracle by trading in a loop within EVM (using re-entrant style flash swap)

    function getTwap(uint256 prevCumulative, uint256 prevTime) external view returns (uint256) {
        uint256 elapsed = block.timestamp - prevTime;
        require(elapsed >= WINDOW, "Window not elapsed");
        // BUG: if attacker dominated the cumulative sum, TWAP is attacker-controlled
        return (priceCumulative - prevCumulative) / elapsed;
    }
}
